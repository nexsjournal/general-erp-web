# -*- coding: utf-8 -*-
"""幂等站点同步：把代码里依赖的 Custom Field / 角色 / Web Form 固化入库。

背景：Customer 扩展字段与 Website Lead 表单此前只在开发机手工创建、未入库，
新站点安装后公海/热点/业绩排行/客户合并引用不存在的列而报错（T01/T02/T03/T07）。
约定：所有此类结构统一经本模块同步，挂 after_install + after_migrate 钩子，幂等可重复。
"""
import frappe

CUSTOMER_FIELDS = [
    ("is_public_pool", "公海客户", "Check", 1),
    ("is_starred", "热点客户（星标）", "Check", 1),
    ("sales_owner", "销售负责人", "Link", 1),
    ("merged_into", "已合并到", "Link", 0),
]
CUSTOMER_COLUMNS = {
    "is_public_pool": "INT(1) NOT NULL DEFAULT 0",
    "is_starred": "INT(1) NOT NULL DEFAULT 0",
    "sales_owner": "VARCHAR(140) DEFAULT NULL",
    "merged_into": "VARCHAR(140) DEFAULT NULL",
}


def sync_customer_fields():
    """Customer 扩展字段同步（幂等，T01）。"""
    for name, label, ftype, in_list in CUSTOMER_FIELDS:
        if frappe.db.get_value("Custom Field", {"dt": "Customer", "fieldname": name}):
            continue
        cf = frappe.new_doc("Custom Field")
        cf.dt = "Customer"
        cf.fieldname = name
        cf.label = label
        cf.fieldtype = ftype
        cf.options = "User" if name == "sales_owner" else "Customer" if name == "merged_into" else None
        cf.insert_after = "territory"
        cf.in_list_view = in_list
        cf.default = "0" if ftype == "Check" else None
        cf.reqd = 0
        cf.translatable = 1
        cf.insert(ignore_permissions=True)
    for col, spec in CUSTOMER_COLUMNS.items():
        frappe.db.sql_ddl("ALTER TABLE `tabCustomer` ADD COLUMN IF NOT EXISTS " + col + " " + spec)
    frappe.db.commit()


ROLES = [
    ("Sales", "销售：看自己的客户/商机/邮件"),
    ("Sales Manager", "销售主管：看本部门下属的客户/邮件（只读）"),
]


SALES_STAGES = [
    ("Prospecting", "初步接触"),
    ("Qualification", "资质确认"),
    ("Proposal", "方案/报价"),
    ("Negotiation", "商务谈判"),
    ("Won", "赢单"),
    ("Lost", "丢单"),
]


def sync_sales_stages():
    """CRM 商机阶段种子数据：Opportunity.sales_stage 默认值 Prospecting 必须存在，否则商机无法创建（真实 P1）。"""
    for name, desc in SALES_STAGES:
        if not frappe.db.exists("Sales Stage", name):
            ss = frappe.new_doc("Sales Stage")
            ss.stage_name = name
            ss.description = desc
            ss.insert(ignore_permissions=True)
    frappe.db.commit()


def sync_roles():
    for name, desc in ROLES:
        if not frappe.db.exists("Role", name):
            r = frappe.new_doc("Role")
            r.role_name = name
            r.description = desc
            r.insert(ignore_permissions=True)
    frappe.db.commit()


def sync_website_lead_form():
    """官网留言 Web Form（/website-lead，T02）：访客提交自动生成 Lead。"""
    if frappe.db.exists("Web Form", {"route": "website-lead"}):
        return
    form = frappe.new_doc("Web Form")
    form.title = "在线留言"
    form.module = "CRM"
    form.doc_type = "Lead"
    form.route = "website-lead"
    form.introduction_text = "<p>留下您的信息，我们会尽快与您联系。/ Leave your message, we will contact you soon.</p>"
    form.login_required = 0
    form.allow_multiple = 1
    form.published = 1
    form.success_message = "提交成功，我们会尽快联系您。/ Thank you, we will contact you soon."
    for fld in [
        ("lead_name", "姓名 / Name", "Data", 1),
        ("email_id", "邮箱 / Email", "Data", 1),
        ("phone", "电话 / Phone", "Data", 0),
        ("company_name", "公司 / Company", "Data", 0),
        ("website", "来源渠道 / Source", "Data", 0),
        ("notes", "留言内容 / Message", "Small Text", 1),
    ]:
        form.append("web_form_fields", {"fieldname": fld[0], "label": fld[1], "fieldtype": fld[2], "reqd": fld[3], "read_only": 0})
    form.insert(ignore_permissions=True)
    frappe.db.commit()


def sync_opportunity_fields():
    """商机批复状态字段（待批复/已批复/待回复，T03 视图基础）。"""
    if not frappe.db.get_value("Custom Field", {"dt": "Opportunity", "fieldname": "approval_status"}):
        cf = frappe.new_doc("Custom Field")
        cf.dt = "Opportunity"
        cf.fieldname = "approval_status"
        cf.label = "批复状态"
        cf.fieldtype = "Select"
        cf.options = chr(10).join(["待批复", "已批复", "待回复"])
        cf.insert_after = "status"
        cf.in_list_view = 1
        cf.reqd = 0
        cf.translatable = 1
        cf.insert(ignore_permissions=True)
    frappe.db.sql_ddl("ALTER TABLE `tabOpportunity` ADD COLUMN IF NOT EXISTS approval_status VARCHAR(40) DEFAULT NULL")
    frappe.db.commit()


def sync_company_fields():
    """企业信息：中英文名称/税号/银行账户（T07）。"""
    for name, label, ftype in [
        ("english_name", "英文名称", "Data"),
        ("bank_name", "开户银行", "Data"),
        ("bank_account", "银行账号", "Data"),
    ]:
        if frappe.db.get_value("Custom Field", {"dt": "Company", "fieldname": name}):
            continue
        cf = frappe.new_doc("Custom Field")
        cf.dt = "Company"
        cf.fieldname = name
        cf.label = label
        cf.fieldtype = ftype
        cf.insert_after = "country"
        cf.reqd = 0
        cf.translatable = 1
        cf.insert(ignore_permissions=True)
    frappe.db.commit()


# ============================================================
# 采购订单审批 Workflow（T03，P0 采购模块）
# ============================================================
PO_WORKFLOW_STATES = [
    ("草稿", "0", "Sales"),
    ("审批中", "0", "Sales Manager"),
    ("已审批", "1", "System Manager"),
    ("已驳回", "0", "Sales"),
]
PO_WORKFLOW_TRANSITIONS = [
    ("草稿", "提交审批", "审批中", "Sales"),
    ("审批中", "审批", "已审批", "Sales Manager"),
    ("审批中", "驳回", "已驳回", "Sales Manager"),
    ("已驳回", "重新提交", "审批中", "Sales"),
]


def _ensure_workflow_states(states):
    """v16: Workflow State 是独立 DocType，Link 引用需先存在。"""
    for state_name, doc_status, role in states:
        if not frappe.db.exists("Workflow State", state_name):
            st = frappe.new_doc("Workflow State")
            st.workflow_state_name = state_name
            st.insert(ignore_permissions=True)
    frappe.db.commit()


def _ensure_workflow_actions(actions):
    """v16: Workflow Action Master 独立 DocType。"""
    for a in set(actions):
        if not frappe.db.exists("Workflow Action Master", a):
            am = frappe.new_doc("Workflow Action Master")
            am.workflow_action_name = a
            am.insert(ignore_permissions=True)
    frappe.db.commit()


def sync_po_workflow():
    """采购订单审批流（v16 语义：独立 State/Action Master + 单角色 Link）。"""
    wf_name = "采购订单审批"
    if frappe.db.exists("Workflow", wf_name):
        return
    _ensure_workflow_states(PO_WORKFLOW_STATES)
    _ensure_workflow_actions([t[1] for t in PO_WORKFLOW_TRANSITIONS])
    wf = frappe.new_doc("Workflow")
    wf.workflow_name = wf_name
    wf.document_type = "Purchase Order"
    wf.workflow_state_field = "workflow_state"
    wf.is_active = 1
    wf.override_status = 0
    wf.send_email_alert = 0
    for state_name, doc_status, role in PO_WORKFLOW_STATES:
        wf.append("states", {
            "state": state_name, "doc_status": doc_status,
            "allow_edit": role, "avoid_status_override": 0, "send_email": 0,
            "is_optional_state": 0, "evaluate_as_expression": 0,
        })
    for state_name, action, next_state, allowed in PO_WORKFLOW_TRANSITIONS:
        wf.append("transitions", {
            "state": state_name, "action": action, "next_state": next_state,
            "allowed": allowed, "allow_self_approval": 1, "send_email_to_creator": 0,
        })
    wf.insert(ignore_permissions=True)
    frappe.db.commit()


# ============================================================
# 商机批复视图 + 状态切换（T03）
# ============================================================
OPP_QUICK_LISTS = [
    ("商机 - 待批复", "待批复"),
    ("商机 - 已批复", "已批复"),
    ("商机 - 待回复", "待回复"),
]


def sync_opportunity_quick_lists():
    """商机三状态筛选视图（v16 无 Quick List doctype，用 List Filter 保存筛选替代，全局可见）。"""
    for title, value in OPP_QUICK_LISTS:
        if frappe.db.exists(
            "List Filter", {"filter_name": title, "reference_doctype": "Opportunity"}
        ):
            continue
        lf = frappe.new_doc("List Filter")
        lf.filter_name = title
        lf.reference_doctype = "Opportunity"
        lf.for_user = ""
        lf.filters = frappe.as_json(
            [{"fieldname": "approval_status", "operator": "=", "value": value}]
        )
        lf.insert(ignore_permissions=True)
    frappe.db.commit()


@frappe.whitelist()
def set_opportunity_approval_status(name, status):
    """商机批复状态切换（待批复→已批复→待回复），留痕。"""
    if status not in ("待批复", "已批复", "待回复"):
        frappe.throw("无效的批复状态")
    doc = frappe.get_doc("Opportunity", name)
    old = doc.approval_status
    doc.approval_status = status
    from frappe.desk.form.utils import add_comment
    add_comment(
        "Opportunity", name,
        "批复状态：{} → {}".format(old or "（空）", status),
        comment_email=frappe.session.user, comment_by=frappe.session.user,
    )
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return True


def sync_mail_account_rate_limits():
    """营销账号频率限制：日发送上限、单收件人上限（T06）。0=不限制。"""
    specs = [
        ("daily_send_limit", "日发送上限", "Int", 0),
        ("per_recipient_limit", "单收件人上限", "Int", 0),
    ]
    for fieldname, label, ftype, in_list in specs:
        if frappe.db.get_value("Custom Field", {"dt": "Mail Account", "fieldname": fieldname}):
            continue
        cf = frappe.new_doc("Custom Field")
        cf.dt = "Mail Account"
        cf.fieldname = fieldname
        cf.label = label
        cf.fieldtype = ftype
        cf.in_list_view = in_list
        cf.reqd = 0
        cf.translatable = 0
        cf.insert(ignore_permissions=True)
    frappe.db.commit()


def sync_mail_fields():
    """Mail 增强字段：分发/归档客户/审批规则（T04）。"""
    specs = [
        ("distributed_to", "已分发给", "Link", "User", 0),
        ("archive_customer", "归档客户", "Link", "Customer", 0),
        ("approval_rule", "审批规则命中", "Data", None, 0),
    ]
    for name, label, ftype, options, in_list in specs:
        if frappe.db.get_value("Custom Field", {"dt": "Mail", "fieldname": name}):
            continue
        cf = frappe.new_doc("Custom Field")
        cf.dt = "Mail"
        cf.fieldname = name
        cf.label = label
        cf.fieldtype = ftype
        cf.options = options
        cf.in_list_view = in_list
        cf.reqd = 0
        cf.translatable = 1
        cf.insert(ignore_permissions=True)
    frappe.db.commit()


def sync_site_setup(with_seed=False):
    """总入口：after_install 与 after_migrate 调用，幂等。"""
    sync_customer_fields()
    sync_sales_stages()
    sync_roles()
    sync_website_lead_form()
    sync_opportunity_fields()
    sync_company_fields()
    sync_po_workflow()
    sync_opportunity_quick_lists()
    sync_mail_account_rate_limits()
    sync_mail_fields()
    if with_seed:
        from general_erp.general_erp.seed_data import seed_base_data
        if frappe.db.exists("DocType", "Port"):
            seed_base_data()


def after_install():
    """安装后：结构同步 + 基础数据播种。"""
    sync_site_setup(with_seed=True)


def after_migrate():
    """migrate 后：仅结构同步（播种只走一次，install 时已做）。"""
    sync_site_setup(with_seed=False)
