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


def sync_site_setup(with_seed=False):
    """总入口：after_install 与 after_migrate 调用，幂等。"""
    sync_customer_fields()
    sync_roles()
    sync_website_lead_form()
    sync_opportunity_fields()
    sync_company_fields()
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
