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


# 岗位角色体系（T-roles，2026-08-29）：岗位 -> 背后原生角色
# 管理员建用户时选岗位（role_profiles），自动带整套原生角色；
# 自研单据/报表权限在 doctype json 里双写到岗位角色上。
ROLE_PROFILES = [
    ("销售", ["Sales", "Sales User", "Desk User"]),
    ("外贸专员", ["Sales", "Sales User", "Sales Manager", "Stock User", "Desk User"]),
    ("采购", ["Purchase User", "Purchase Manager", "Desk User"]),
    ("库存", ["Stock User", "Stock Manager", "Desk User"]),
    ("财务", ["Accounts User", "Accounts Manager", "Desk User"]),
    ("总经理", ["Sales Manager", "Purchase Manager", "Stock Manager", "Accounts Manager", "Desk User"]),
    ("系统管理员", ["System Manager", "Desk User"]),
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


def sync_role_profiles():
    """岗位角色 + Role Profile 幂等同步（T-roles）。"""
    for name, native in ROLE_PROFILES:
        if not frappe.db.exists("Role", name):
            r = frappe.new_doc("Role")
            r.role_name = name
            r.description = "岗位角色（选此岗位自动带对应权限）"
            r.desk_access = 1
            r.insert(ignore_permissions=True)
        if frappe.db.exists("Role Profile", name):
            frappe.delete_doc("Role Profile", name, force=True)
        frappe.get_doc({
            "doctype": "Role Profile",
            "role_profile": name,
            "roles": [{"role": rn} for rn in [name] + native],
        }).insert(ignore_permissions=True)
    frappe.db.commit()


def sync_currency_display():
    """金额显示口径（T-currency，2026-08-29）：CNY 符号=元且显示在数字右侧（382,000.00 元）；数字卡默认全额显示（不缩写成"千"）。"""
    if frappe.db.exists("Currency", "CNY"):
        if not frappe.db.get_value("Currency", "CNY", "symbol"):
            frappe.db.set_value("Currency", "CNY", "symbol", "元")
        if not frappe.db.get_value("Currency", "CNY", "symbol_on_right"):
            frappe.db.set_value("Currency", "CNY", "symbol_on_right", 1)
    for c in frappe.get_all("Number Card", fields=["name", "show_full_number"]):
        if not c["show_full_number"]:
            frappe.db.set_value("Number Card", c["name"], "show_full_number", 1)
    frappe.db.commit()
    frappe.clear_cache()


def sync_user_login_settings():
    """国内习惯建号（T-user-login）：允许用户名登录 + 邮箱改非必填。

    邮箱在 frappe 是身份锚点且 meta reqd=1（_validate_mandatory 层拦截，
    早于 validate()）。这里用 Property Setter 把 User.email.reqd 降 0（非侵入、落库），
    配合 overwrite/user/user.py 的无邮箱分支（name 取 username）实现纯用户名建号。
    有邮箱用户行为不受影响（validate 内仍走 email=name 同步与格式校验）。
    """
    # 1. 用户名登录开关（frappe 原生，auth.find_by_credentials 读此值）
    ss = frappe.get_doc("System Settings")
    if not ss.allow_login_using_user_name:
        ss.allow_login_using_user_name = 1
        ss.save(ignore_permissions=True)
    # 2. 邮箱非必填（Property Setter，幂等）
    ps_name = "User-email-reqd-zero"
    if not frappe.db.exists("Property Setter", ps_name):
        frappe.get_doc({
            "doctype": "Property Setter",
            "property_setter": ps_name,
            "doc_type": "User",
            "doctype_or_field": "DocField",
            "field_name": "email",
            "property": "reqd",
            "property_type": "Check",
            "value": "0",
        }).insert(ignore_permissions=True)
    frappe.db.commit()
    frappe.clear_cache("User")


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
# 多公司 company 字段（T2-10）：自定义业务单据支持多公司部署
# ============================================================
COMPANY_FIELD_DOCTYPES = [
    "Bulk Email",
    "Customer Follow Up",
    "Expense Reimbursement",
    "Inspection Order",
    "Mail",
    "Export Shipment",
    "Trade Document",
]


def sync_multi_company_fields():
    """给 app 自定义业务单据加 company Link 字段（幂等，Link→Company，非必填）。"""
    for dt in COMPANY_FIELD_DOCTYPES:
        if not frappe.db.exists("DocType", dt):
            continue
        if frappe.db.get_value("Custom Field", {"dt": dt, "fieldname": "company"}):
            continue
        cf = frappe.new_doc("Custom Field")
        cf.dt = dt
        cf.fieldname = "company"
        cf.label = "公司"
        cf.fieldtype = "Link"
        cf.options = "Company"
        cf.reqd = 0
        cf.in_list_view = 1
        cf.insert(ignore_permissions=True)
    frappe.db.commit()


# ============================================================
# 生产任务单审批流（T2-14）：Production Plan 复用 app 审批模式
# 草稿→审批中→已审批（docstatus 0→0→1），驳回→已驳回
# ============================================================
PP_WORKFLOW_STATES = [
    ("草稿", "0", "Stock Manager"),
    ("审批中", "0", "Purchase Manager"),
    ("已审批", "1", "Purchase Manager"),
    ("已驳回", "0", "Stock Manager"),
]
PP_WORKFLOW_TRANSITIONS = [
    ("草稿", "提交审批", "审批中", "Stock Manager"),
    ("审批中", "审批", "已审批", "Purchase Manager"),
    ("审批中", "驳回", "已驳回", "Purchase Manager"),
    ("已驳回", "重新提交", "审批中", "Stock Manager"),
]


def sync_production_plan_workflow():
    """生产任务单（Production Plan）审批流，与采购/费用审批同一模式。"""
    if not frappe.db.exists("DocType", "Production Plan"):
        return
    _ensure_pp_permissions()
    wf_name = "生产任务单审批"
    if frappe.db.exists("Workflow", wf_name):
        wf = frappe.get_doc("Workflow", wf_name)
        changed = False
        for s in wf.states:
            want = dict((x[0], x[2]) for x in PP_WORKFLOW_STATES).get(s.state)
            if want and s.allow_edit != want:
                s.allow_edit = want
                changed = True
        for t in wf.transitions:
            want = dict((x[0], x[3]) for x in PP_WORKFLOW_TRANSITIONS).get(t.state)
            if want and t.allowed != want:
                t.allowed = want
                changed = True
        if changed:
            wf.flags.ignore_permissions = True
            wf.save()
            frappe.db.commit()
        return
    _ensure_workflow_states(PP_WORKFLOW_STATES)
    _ensure_workflow_actions([t[1] for t in PP_WORKFLOW_TRANSITIONS])
    wf = frappe.new_doc("Workflow")
    wf.workflow_name = wf_name
    wf.document_type = "Production Plan"
    wf.workflow_state_field = "workflow_state"
    wf.is_active = 1
    wf.override_status = 0
    wf.send_email_alert = 0
    for state_name, doc_status, role in PP_WORKFLOW_STATES:
        wf.append("states", {
            "state": state_name, "doc_status": doc_status,
            "allow_edit": role, "avoid_status_override": 0, "send_email": 0,
            "is_optional_state": 0, "evaluate_as_expression": 0,
        })
    for state_name, action, next_state, allowed in PP_WORKFLOW_TRANSITIONS:
        wf.append("transitions", {
            "state": state_name, "action": action, "next_state": next_state,
            "allowed": allowed, "allow_self_approval": 1, "send_email_to_creator": 0,
        })
    wf.insert(ignore_permissions=True)
    frappe.db.commit()


def _ensure_pp_permissions():
    """Production Plan 权限：现有业务角色接入（走 CDP 全量拷贝语义，不塌 base）。
    仓库=建单/提交，采购经理=审批/驳回，系统管理=全权。"""
    from frappe.permissions import setup_custom_perms, add_permission
    setup_custom_perms("Production Plan")
    for role, perms in [
        ("Stock Manager", {"write": 1, "create": 1, "submit": 1}),
        ("Purchase Manager", {"write": 1, "submit": 1, "cancel": 1, "amend": 1}),
        ("System Manager", {"write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1, "amend": 1}),
    ]:
        row = frappe.db.get_value(
            "Custom DocPerm",
            {"parent": "Production Plan", "role": role, "permlevel": 0, "if_owner": 0},
            "name",
        )
        if not row:
            add_permission("Production Plan", role, 0, ptype="read")
            row = frappe.db.get_value(
                "Custom DocPerm",
                {"parent": "Production Plan", "role": role, "permlevel": 0, "if_owner": 0},
                "name",
            )
        if not row:
            continue
        for k, v in perms.items():
            frappe.db.set_value("Custom DocPerm", row, k, v)
    frappe.db.commit()
    frappe.clear_cache(doctype="Production Plan")


def _ensure_pp_workflow_roles():
    """生产任务单权限同步（与 _ensure_pp_permissions 同体，入口拆分便于阅读）。"""
    _ensure_pp_permissions()


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
def sync_customer_list_filters():
    """客户三视图（T2-09）：我的客户 / 公海客户 / 热点客户（List Filter，与商机三视图同机制）。"""
    for title, filters in [
        ("我的客户", [{"fieldname": "sales_owner", "operator": "=", "value": "me"}]),
        ("公海客户", [{"fieldname": "is_public_pool", "operator": "=", "value": 1}]),
        ("热点客户", [{"fieldname": "is_starred", "operator": "=", "value": 1}]),
    ]:
        if frappe.db.exists("List Filter", {"filter_name": title, "reference_doctype": "Customer"}):
            continue
        lf = frappe.new_doc("List Filter")
        lf.filter_name = title
        lf.reference_doctype = "Customer"
        lf.for_user = ""
        lf.filters = frappe.as_json(filters)
        lf.insert(ignore_permissions=True)
    frappe.db.commit()


def sync_opportunity_defaults():
    """商机默认值（T2-02）：opportunity_from=Customer、opportunity_type=Sales，避免新建首崩。"""
    frappe.db.sql("update tabDocField set `default`='Customer' where parent='Opportunity' and fieldname='opportunity_from' and (ifnull(`default`,'')='')")
    frappe.db.sql("update tabDocField set `default`='Sales' where parent='Opportunity' and fieldname='opportunity_type' and (ifnull(`default`,'')='')")
    frappe.db.commit()


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
    """Mail 增强字段：分发/归档客户/审批规则（T04）+ 发送跟踪（T08）。"""
    specs = [
        ("distributed_to", "已分发给", "Link", "User", 0),
        ("archive_customer", "归档客户", "Link", "Customer", 0),
        ("approval_rule", "审批规则命中", "Data", None, 0),
        ("track", "发送跟踪", "Check", None, 0),
        ("tracking_id", "跟踪ID", "Data", None, 0),
        ("opened", "已打开", "Check", None, 0),
        ("clicked", "已点击", "Check", None, 0),
        ("opened_at", "打开时间", "Datetime", None, 0),
        ("clicked_at", "点击时间", "Datetime", None, 0),
        ("from_address", "发件地址", "Data", None, 0),
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


def sync_lead_fields():
    """线索被分发人字段（线索统计报表 / assign_lead 分发逻辑依赖）。"""
    specs = [
        ("assigned_to", "被分发人", "Link", "User", 1),
        ("assigned_at", "分发时间", "Datetime", None, 0),
    ]
    for name, label, ftype, options, in_list in specs:
        if frappe.db.get_value("Custom Field", {"dt": "Lead", "fieldname": name}):
            continue
        cf = frappe.new_doc("Custom Field")
        cf.dt = "Lead"
        cf.fieldname = name
        cf.label = label
        cf.fieldtype = ftype
        cf.options = options
        cf.in_list_view = in_list
        cf.reqd = 0
        cf.translatable = 1
        cf.insert(ignore_permissions=True)
    frappe.db.commit()


EXPENSE_WORKFLOW_STATES = [
    ("草稿", "0", "System Manager"),
    ("审批中", "0", "System Manager"),
    ("已审批", "1", "System Manager"),
    ("已驳回", "0", "System Manager"),
]
EXPENSE_WORKFLOW_TRANSITIONS = [
    ("草稿", "提交审批", "审批中", "System Manager"),
    ("审批中", "审批", "已审批", "System Manager"),
    ("审批中", "驳回", "已驳回", "System Manager"),
    ("已驳回", "重新提交", "审批中", "System Manager"),
]


def sync_expense_workflow():
    """费用报销审批流（草稿→审批中→已审批/已驳回，与 app 内 workflow JSON 一致）。"""
    wf_name = "费用报销审批"
    if frappe.db.exists("Workflow", wf_name):
        return
    _ensure_workflow_states(EXPENSE_WORKFLOW_STATES)
    _ensure_workflow_actions([t[1] for t in EXPENSE_WORKFLOW_TRANSITIONS])
    wf = frappe.new_doc("Workflow")
    wf.workflow_name = wf_name
    wf.document_type = "Expense Reimbursement"
    wf.workflow_state_field = "workflow_state"
    wf.is_active = 1
    wf.override_status = 0
    wf.send_email_alert = 0
    for state_name, doc_status, role in EXPENSE_WORKFLOW_STATES:
        wf.append("states", {
            "state": state_name, "doc_status": doc_status,
            "allow_edit": role, "avoid_status_override": 0, "send_email": 0,
            "is_optional_state": 0, "evaluate_as_expression": 0,
        })
    for state_name, action, next_state, allowed in EXPENSE_WORKFLOW_TRANSITIONS:
        wf.append("transitions", {
            "state": state_name, "action": action, "next_state": next_state,
            "allowed": allowed, "allow_self_approval": 1, "send_email_to_creator": 0,
        })
    wf.insert(ignore_permissions=True)
    frappe.db.commit()



def sync_report_workspace():
    """报表中心 Workspace 同步（幂等）：保证 7 个业务报表挂在"经营与运营"卡片下。"""
    import os
    import json
    ws_name = "报表中心"
    if not frappe.db.exists("Workspace", ws_name):
        return
    base = os.path.join(os.path.dirname(__file__), "..", "workspace", ws_name, ws_name + ".json")
    base = os.path.normpath(base)
    if not os.path.exists(base):
        return
    with open(base, encoding="utf-8") as f:
        spec = json.load(f)
    doc = frappe.get_doc("Workspace", ws_name)
    # 按 spec 顺序重建 links（spec 是事实源；DB 里多出的旧链接删除）
    spec_links = spec.get("links", [])
    for i in range(len(doc.links) - 1, -1, -1):
        doc.links[i].remove()
    for l in spec_links:
        doc.append("links", l)
    doc.flags.ignore_permissions = True
    doc.flags.ignore_version = True
    doc.save()
    frappe.db.commit()


def sync_site_setup(with_seed=False):
    """总入口：after_install 与 after_migrate 调用，幂等。"""
    sync_customer_fields()
    sync_sales_stages()
    sync_roles()
    sync_role_profiles()
    sync_currency_display()
    sync_user_login_settings()
    sync_website_lead_form()
    sync_opportunity_fields()
    sync_company_fields()
    sync_multi_company_fields()
    sync_production_plan_workflow()
    sync_po_workflow()
    sync_opportunity_quick_lists()
    sync_customer_list_filters()
    sync_opportunity_defaults()
    sync_mail_account_rate_limits()
    sync_mail_fields()
    sync_lead_fields()
    sync_expense_workflow()
    sync_report_workspace()
    if with_seed:
        from general_erp.seed_data import seed_base_data
        if frappe.db.exists("DocType", "Port"):
            seed_base_data()


def after_install():
    """安装后：结构同步 + 基础数据播种。"""
    sync_site_setup(with_seed=True)


def after_migrate():
    """migrate 后：仅结构同步（播种只走一次，install 时已做）。"""
    sync_site_setup(with_seed=False)
