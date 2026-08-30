# -*- coding: utf-8 -*-
"""邮件增强操作（T04）：自动审批规则 / 分发 / 建档 / 归档 / 导出 / 下属邮件。"""
import csv
import io

import frappe
from frappe import _
from frappe.utils import now_datetime

QUOTE_KEYWORDS = ("报价", "价格", "PI", "quote", "price", "USD", "美元")

APPROVE_ROLES = ("Sales Manager", "System Manager")
MANAGER_ROLES = ("Sales Manager", "System Manager")
EXPORT_ROLES = ("Accounts Manager", "Sales Manager", "System Manager")


def _require_roles(roles, action):
    if not set(roles) & set(frappe.get_roles()):
        frappe.throw(_("无{0}权限").format(action), frappe.PermissionError)


def _company_email_domains():
    """公司邮箱域名（用于判断内发/外发）。"""
    domains = set()
    for row in frappe.get_all("Mail Account", fields=["email_id"], limit=50):
        if row.email_id and "@" in row.email_id:
            domains.add(row.email_id.split("@")[-1].lower())
    return domains


def should_require_approval(subject, body, recipients):
    """判断外发邮件是否命中审批规则，返回命中的规则描述（None=无需审批）。"""
    text = ((subject or "") + " " + (body or "")).lower()
    has_quote = any(k.lower() in text for k in QUOTE_KEYWORDS)
    domains = _company_email_domains()
    external = False
    if recipients:
        r = (recipients or "").strip().lower()
        # 内部用户之间互发不算外发（内部协作邮件）
        is_internal_user = frappe.db.exists("User", {"name": r, "enabled": 1})
        if not is_internal_user and "@" in r:
            domain = r.split("@")[-1]
            if domain and domains and domain not in domains:
                external = True
    if has_quote:
        return "含报价内容"
    if external:
        return "外发（非公司域）"
    return None


@frappe.whitelist()
def auto_approval_check(name):
    """发送后自动审批检查：命中规则则置待审批，否则放行。返回 {approved, rule}。"""
    m = frappe.get_doc("Mail", name)
    if m.folder != "已发送":
        return {"approved": True, "rule": None}
    rule = should_require_approval(m.subject, m.body, m.recipient)
    if rule:
        m.status = "待审批"
        m.approval_rule = rule
        m.save(ignore_permissions=True)
        from frappe.desk.form.utils import add_comment
        add_comment("Mail", name, "自动审批规则命中：{}，已转待审批。".format(rule),
                    comment_email=frappe.session.user, comment_by=frappe.session.user)
        frappe.db.commit()
        return {"approved": False, "rule": rule}
    m.status = "已处理"
    m.save(ignore_permissions=True)
    frappe.db.commit()
    return {"approved": True, "rule": None}


@frappe.whitelist()
def approve_mail(name):
    """审批通过：待审批 → 已处理。仅限销售主管/系统管理员。"""
    _require_roles(APPROVE_ROLES, "邮件审批")
    m = frappe.get_doc("Mail", name)
    if m.status != "待审批":
        frappe.throw(_("仅待审批邮件可审批"))
    m.status = "已处理"
    from frappe.desk.form.utils import add_comment
    add_comment("Mail", name, "审批通过。",
                comment_email=frappe.session.user, comment_by=frappe.session.user)
    m.save(ignore_permissions=True)
    frappe.db.commit()
    return True


@frappe.whitelist()
def distribute_mail(name, to_user):
    """邮件分发给同事处理：复制一条待处理收件到对方收件箱，留痕。"""
    _require_roles(MANAGER_ROLES, "邮件分发")
    if not frappe.db.exists("User", to_user):
        frappe.throw(_("目标用户不存在"))
    m = frappe.get_doc("Mail", name)
    inbox = frappe.new_doc("Mail")
    inbox.update({
        "subject": "[分发] " + (m.subject or ""),
        "folder": "收件箱",
        "sender": frappe.session.user,
        "recipient": to_user,
        "body": m.body,
        "status": "待处理",
        "related_doctype": m.related_doctype,
        "related_name": m.related_name,
        "sent_at": now_datetime(),
    })
    inbox.insert(ignore_permissions=True)
    m.distributed_to = to_user
    m.save(ignore_permissions=True)
    frappe.db.commit()
    return inbox.name


@frappe.whitelist()
def file_mail_to_customer(name, customer):
    """邮件建档：关联到客户，并自动写一条客户跟进留痕。"""
    if not frappe.db.exists("Customer", customer):
        frappe.throw(_("客户不存在"))
    m = frappe.get_doc("Mail", name)
    m.archive_customer = customer
    m.related_doctype = "Customer"
    m.related_name = customer
    m.save(ignore_permissions=True)
    fu = frappe.new_doc("Customer Follow Up")
    fu.update({
        "customer": customer,
        "follow_type": "邮件",
        "follow_date": now_datetime().date(),
        "content": "邮件建档：" + (m.subject or ""),
    })
    fu.insert(ignore_permissions=True)
    frappe.db.commit()
    return True


@frappe.whitelist()
def archive_mail(name, folder="已归档"):
    """归档：移入归档文件夹（记录恢复信息）。"""
    m = frappe.get_doc("Mail", name)
    m.restore_folder = m.folder
    m.restore_status = m.status
    m.folder = folder
    m.save(ignore_permissions=True)
    frappe.db.commit()
    return True


@frappe.whitelist()
def export_mails(folder=None, status=None, limit=500):
    """邮件列表导出 CSV，返回下载 URL。仅限财务/主管/管理员，上限 5000 条。"""
    _require_roles(EXPORT_ROLES, "邮件导出")
    limit = min(int(limit or 500), 5000)
    rows = frappe.get_all(
        "Mail",
        filters={k: v for k, v in (("folder", folder), ("status", status)) if v},
        fields=["name", "subject", "folder", "status", "sender", "recipient",
                "sent_at", "creation", "archive_customer"],
        order_by="modified desc",
        limit_page_length=limit,
    )
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["主题", "文件夹", "状态", "发件人", "收件人", "发送时间", "归档客户"])
    for r in rows:
        t = r.sent_at or r.creation or ""
        ts = t.isoformat(sep=" ") if hasattr(t, "isoformat") else str(t)
        w.writerow([r.subject, r.folder, r.status, r.sender, r.recipient or "", ts,
                    r.archive_customer or ""])
    fname = "mails-export-{}.csv".format(frappe.utils.nowdate())
    content = "\\ufeff" + out.getvalue()
    fdoc = frappe.get_doc({
        "doctype": "File",
        "file_name": fname,
        "content": content.encode("utf-8"),
        "is_private": 1,
    })
    fdoc.save(ignore_permissions=True)
    frappe.db.commit()
    return fdoc.file_url


@frappe.whitelist()
def get_subordinate_mails(limit=100):
    """主管查看本部门下属的邮件（只读）：按 User.erp_department 下属用户聚合。"""
    user = frappe.session.user
    # 仅主管可见下属邮件；非主管返回空（防止下属看到上级邮件）
    manager_roles = {"Sales Manager", "Purchase Manager", "Stock Manager", "Accounts Manager", "System Manager"}
    if frappe.session.user != "Administrator" and not (set(frappe.get_roles()) & manager_roles):
        return []
    my_dept = frappe.db.get_value("User", user, "erp_department")
    if not my_dept:
        return []
    try:
        return frappe.db.sql("""
        SELECT m.name, m.subject, m.folder, m.status, m.sender, m.recipient,
               m.sent_at, u.full_name AS sender_name
        FROM `tabMail` m
        LEFT JOIN `tabUser` u ON u.name = m.sender
        WHERE m.sender IN (
            SELECT u2.name FROM `tabUser` u2
            WHERE u2.erp_department = %s AND u2.enabled = 1
        )
        ORDER BY m.modified DESC
        LIMIT %s
        """, (my_dept, int(limit or 100)), as_dict=True)
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_subordinate_mails")
        frappe.throw(_("加载下属邮件失败，请联系管理员"))
