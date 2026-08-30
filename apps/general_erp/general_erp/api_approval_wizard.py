# -*- coding: utf-8 -*-
"""T-approval-wizard: 审批流程自助设置向导 API。

把"给某单据配审批流"变成三问式操作（选单据 / 定审批链 / 智能选项），
底层生成标准 frappe Workflow 单据（不造新引擎、不碰 frappe 源码）：
- 审批人按角色：v16 的 allowed 是单角色 Link，多角色=多行同流转
  （与现有三条预置流程同构，按钮由 get_transitions 按当前用户角色过滤）
- 多级审批：每级一个独立状态（审批1/审批2/审批3），防绕过守卫天然兼容
- 小额免批：金额字段低于阈值时，发起人可选"免批通过"直接生效（流转 condition）
- 超时催办：自定义字段 approval_timeout_hours，daily scheduler 发系统通知
仅 系统管理员/System Manager/流程设计 角色可操作（API 内二次校验）。
"""
import json

import frappe
from frappe import _

# 向导可选单据 → 金额字段（小额免批条件用；None=无金额字段，不支持免批）
SUPPORTED_DOC_TYPES = [
	("Sales Order", "销售订单", "grand_total"),
	("Sales Invoice", "销售发票", "grand_total"),
	("Purchase Order", "采购订单", "grand_total"),
	("Purchase Invoice", "采购发票", "grand_total"),
	("Payment Entry", "付款单", "paid_amount"),
	("Expense Claim", "费用报销", "total_claim_amount"),
	("Delivery Note", "交货单", "grand_total"),
	("Production Plan", "生产计划", None),
]
# 向导可选角色（显示名 → 实际 Role 名）
ROLE_CHOICES = [
	("销售", "Sales User"),
	("外贸专员", "外贸专员"),
	("采购", "Purchase User"),
	("库存", "Stock User"),
	("财务", "Accounts User"),
	("销售经理", "Sales Manager"),
	("采购经理", "Purchase Manager"),
	("库存经理", "Stock Manager"),
	("财务经理", "Accounts Manager"),
	("总经理", "总经理"),
]
DESIGN_ROLES = ("System Manager", "系统管理员", "流程设计")
START_STATE = "草稿"
FINAL_STATE = "已审批"
REJECT_STATE = "已驳回"
MAX_LEVELS = 3


def _check_design_permission():
	if not set(frappe.get_roles()) & set(DESIGN_ROLES):
		frappe.throw(_("只有系统管理员或流程设计角色可以管理审批流程"))


def _role_map():
	return dict(ROLE_CHOICES)


def _role_label(role):
	for label, value in ROLE_CHOICES:
		if value == role:
			return label
	return role


@frappe.whitelist()
def get_options():
	"""向导下拉数据：单据类型 + 角色。"""
	_check_design_permission()
	return {
		"doc_types": [
			{"label": label, "value": dt, "amount_field": af}
			for dt, label, af in SUPPORTED_DOC_TYPES if frappe.db.exists("DocType", dt)
		],
		"roles": [{"label": label, "value": value} for label, value in ROLE_CHOICES],
	}


def _summarize(wf):
	"""流程摘要：发起角色 + 审批链（按状态出现顺序）。"""
	start_roles, chain = [], []
	for s in wf.states:
		if s.state.startswith("审批"):
			roles = sorted({t.allowed for t in wf.transitions
			                if t.state == s.state and t.next_state not in (REJECT_STATE,)})
			chain.append({"state": s.state, "roles": roles,
			              "role_labels": [_role_label(r) for r in roles]})
	for t in wf.transitions:
		if t.next_state.startswith("审批") and t.state in (START_STATE, REJECT_STATE):
			if t.allowed not in start_roles:
				start_roles.append(t.allowed)
	return {
		"name": wf.name,
		"document_type": wf.document_type,
		"dt_label": frappe.db.get_value("DocType", wf.document_type, "name") or wf.document_type,
		"is_active": wf.is_active,
		"modified": str(wf.modified),
		"start_roles": start_roles,
		"start_role_labels": [_role_label(r) for r in start_roles],
		"chain": chain,
		"min_approval_amount": wf.get("min_approval_amount"),
		"approval_timeout_hours": wf.get("approval_timeout_hours"),
	}


@frappe.whitelist()
def list_workflows():
	"""流程清单（组织管理→审批设置）。"""
	_check_design_permission()
	out = []
	for w in frappe.get_all("Workflow", fields=["name"], order_by="modified desc"):
		out.append(_summarize(frappe.get_doc("Workflow", w.name)))
	return out


@frappe.whitelist()
def get_workflow_detail(wf_name):
	_check_design_permission()
	return _summarize(frappe.get_doc("Workflow", wf_name))


@frappe.whitelist()
def save_workflow(wf_name, document_type, start_roles, levels,
                  min_approval_on, min_approval_amount, timeout_hours, is_active=1):
	"""向导保存：全量重建一条 Workflow。

	start_roles: JSON list 角色名；levels: JSON list [{"roles": [角色名,...]}]，1~3 级。
	同单据已存在流程时覆盖更新（向导=该单据流程的唯一配置入口）。
	"""
	_check_design_permission()
	start_roles = json.loads(start_roles) if isinstance(start_roles, str) else (start_roles or [])
	levels = json.loads(levels) if isinstance(levels, str) else (levels or [])
	start_roles = [r for r in (start_roles or []) if r]
	levels = [[r for r in (lv.get("roles") or []) if r] for lv in (levels or [])]
	levels = [lv for lv in levels if lv]
	if not start_roles:
		frappe.throw(_("发起角色不能为空"))
	if not levels:
		frappe.throw(_("至少需要一级审批"))
	if len(levels) > MAX_LEVELS:
		frappe.throw(_(f"最多支持 {MAX_LEVELS} 级审批"))

	amount_field = dict((dt, af) for dt, _l, af in SUPPORTED_DOC_TYPES).get(document_type)
	if not frappe.db.exists("DocType", document_type):
		frappe.throw(_("单据类型不存在: {0}").format(document_type))
	if amount_field is None:
		frappe.throw(_("暂不支持该单据类型（或该单据没有金额字段，不支持小额免批）"))
	all_roles = start_roles + [r for lv in levels for r in lv]
	for role in all_roles:
		if not frappe.db.exists("Role", role):
			frappe.throw(_("角色不存在: {0}").format(role))

	min_amount = float(min_approval_amount) if (min_approval_on and min_approval_amount) else None

	dt_label = frappe.db.get_value("DocType", document_type, "name") or document_type
	wf_name = "审批-{0}".format(dt_label)
	# 同单据已有流程 → 整体删除重建（向导=该单据流程唯一配置入口；防子表残留行 Link 校验错乱）
	if frappe.db.exists("Workflow", wf_name):
		old_doc = frappe.get_doc("Workflow", wf_name)
		old_doc.flags.ignore_permissions = True
		old_doc.delete()
		frappe.db.commit()
	doc = frappe.new_doc("Workflow")
	doc.workflow_name = wf_name
	doc.document_type = document_type
	doc.workflow_state_field = "workflow_state"
	doc.is_active = 0

	# 状态
	doc.append("states", {"state": START_STATE, "doc_status": "0",
	                      "allow_edit": start_roles[0]})
	for i, lv in enumerate(levels, start=1):
		doc.append("states", {"state": "审批{0}".format(i), "doc_status": "1",
		                      "allow_edit": lv[0]})
	doc.append("states", {"state": FINAL_STATE, "doc_status": "1",
	                      "allow_edit": "System Manager"})
	doc.append("states", {"state": REJECT_STATE, "doc_status": "1",
	                      "allow_edit": start_roles[0]})

	# 发起（每个发起角色一行）
	for role in start_roles:
		doc.append("transitions", {"state": START_STATE, "next_state": "审批1",
		                          "action": "提交审批", "allowed": role})
		doc.append("transitions", {"state": REJECT_STATE, "next_state": "审批1",
		                          "action": "重新提交", "allowed": role})
	# 每级审批：通过→下一级/已审批；驳回→已驳回（每角色一行）
	for i, lv in enumerate(levels, start=1):
		next_state = "审批{0}".format(i + 1) if i < len(levels) else FINAL_STATE
		for role in lv:
			doc.append("transitions", {"state": "审批{0}".format(i), "next_state": next_state,
			                          "action": "审批通过", "allowed": role})
			doc.append("transitions", {"state": "审批{0}".format(i), "next_state": REJECT_STATE,
			                          "action": "驳回", "allowed": role})
	# 小额免批：发起人草稿态可选"免批通过"（condition 由引擎按单据金额求值）
	if min_amount and amount_field:
		for role in start_roles:
			doc.append("transitions", {
				"state": START_STATE, "next_state": FINAL_STATE, "action": "免批通过",
				"allowed": role,
				"condition": "float(doc.get('{0}') or 0) < {1}".format(amount_field, min_amount)})

	doc.save()
	# 向导扩展字段（首次保存后字段已建，二次保存写值）
	doc.min_approval_amount = min_amount
	doc.approval_timeout_hours = int(float(timeout_hours or 0)) or None
	doc.is_active = 1 if is_active else 0
	doc.flags.ignore_permissions = True
	doc.save()
	frappe.db.commit()
	# 同一单据只允许一个生效流程：把同 doctype 的其他 workflow 置停用（显式，避免脏状态）
	for other in frappe.get_all("Workflow", filters={
				"document_type": document_type, "is_active": 1, "name": ["!=", doc.name]}, pluck="name"):
		try:
			o = frappe.get_doc("Workflow", other)
			o.is_active = 0
			o.flags.ignore_permissions = True
			o.save()
		except Exception:
			pass
	frappe.db.commit()
	frappe.clear_cache()
	return _summarize(frappe.get_doc("Workflow", doc.name))


@frappe.whitelist()
def set_workflow_active(wf_name, is_active):
	_check_design_permission()
	doc = frappe.get_doc("Workflow", wf_name)
	doc.is_active = 1 if is_active else 0
	doc.save()
	frappe.db.commit()
	frappe.clear_cache()
	return {"name": wf_name, "is_active": doc.is_active}


@frappe.whitelist()
def delete_workflow(wf_name):
	_check_design_permission()
	doc = frappe.get_doc("Workflow", wf_name)
	if doc.is_active:
		frappe.throw(_("请先停用流程再删除"))
	doc.delete()
	frappe.db.commit()
	frappe.clear_cache()
	return {"deleted": wf_name}


@frappe.whitelist()
def get_my_approvals():
	"""待我审批（所有登录用户可见；按等待时长倒序，超 24h 标 urgent）。"""
	rows = frappe.get_all("Workflow Action",
		filters={"status": "Open"},
		fields=["name", "reference_doctype", "reference_name",
		        "workflow_state", "permitted_roles", "creation"],
		order_by="creation asc", limit=200)
	my_roles = set(frappe.get_roles())
	out = []
	for r in rows:
		if not r.workflow_state or not r.workflow_state.startswith("审批"):
			continue
		permitted = {x.strip() for x in (r.permitted_roles or "").split(",") if x.strip()}
		if not (permitted & my_roles):
			continue
		try:
			doc = frappe.get_doc(r.reference_doctype, r.reference_name)
			amount_field = dict((dt, af) for dt, _l, af in SUPPORTED_DOC_TYPES).get(r.reference_doctype)
			amount = doc.get(amount_field) if amount_field else None
		except Exception:
			continue
		age_h = int((frappe.utils.now_datetime() - r.creation).total_seconds() // 3600)
		out.append({
			"name": r.reference_name,
			"doctype": r.reference_doctype,
			"doctype_label": frappe.db.get_value("DocType", r.reference_doctype, "name") or r.reference_doctype,
			"state": r.workflow_state,
			"amount": amount,
			"age_hours": age_h,
			"urgent": age_h >= 24,
			"url": "/app/{0}/{1}".format(frappe.scrub(r.reference_doctype), r.reference_name),
		})
	out.sort(key=lambda x: -x["age_hours"])
	return out

