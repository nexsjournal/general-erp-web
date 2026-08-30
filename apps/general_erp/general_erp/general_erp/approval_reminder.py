# -*- coding: utf-8 -*-
"""T-approval-wizard: 审批超时催办（daily scheduler）。

扫所有活跃 Workflow 配置的 approval_timeout_hours，
对停留超过该时长的"审批中"单据给审批人（permitted_roles 子表角色持有者）发系统通知，
每个单据每天最多催一次（按日期去重，防刷屏）。
"""
import frappe


def remind_approval_timeout():
	"""每日 09:30 触发：超时的审批单据催办。"""
	from frappe.model.workflow import get_workflow_name

	reminded = 0
	rows = frappe.db.get_all(
		"Workflow Action",
		filters={"status": "Open", "workflow_state": ["like", "审批%"]},
		fields=["name", "reference_doctype", "reference_name", "workflow_state", "creation"],
	)
	# permitted_roles 是子表（Table MultiSelect），批量查子表拿每个 action 的角色
	roles_map = {}
	if rows:
		for x in frappe.get_all("Workflow Action Permitted Role",
			filters={"parenttype": "Workflow Action", "parent": ["in", [r.name for r in rows]]},
			fields=["parent", "role"]):
			roles_map.setdefault(x.parent, set()).add(x.role)
	seen = set()
	for r in rows:
		if not r.workflow_state or not r.workflow_state.startswith("审批"):
			continue
		key = (r.reference_doctype, r.reference_name, r.workflow_state)
		if key in seen:
			continue
		seen.add(key)
		wf_name = get_workflow_name(r.reference_doctype)
		if not wf_name:
			continue
		timeout_h = frappe.db.get_value("Workflow", wf_name, "approval_timeout_hours")
		if not timeout_h:
			continue
		age_h = (frappe.utils.now_datetime() - r.creation).total_seconds() // 3600
		if age_h < timeout_h:
			continue
		# 当天已催过则跳过（redis cache 按日期 key 去重）
		today = frappe.utils.today()
		dedup_key = "approval_remind:{0}:{1}:{2}".format(r.reference_doctype, r.reference_name, today)
		if frappe.cache.get_value(dedup_key):
			continue
		permitted = roles_map.get(r.name, set())
		if not permitted:
			continue
		# 找持有这些角色的活跃用户
		users = set()
		for role in permitted:
			for u in frappe.get_all("Has Role", filters={"role": role, "parenttype": "User"},
			                       fields=["parent"]):
				try:
					if frappe.db.get_value("User", u.parent, "enabled"):
						users.add(u.parent)
				except Exception:
					pass
		if not users:
			continue
		title = "审批超时提醒"
		desc = (f"单据 {r.reference_name} 已在「{r.workflow_state}」停留 "
               f"{age_h // 24} 天 {age_h % 24} 小时（超时 {timeout_h} 小时），请尽快处理。")
		for user in users:
			frappe.get_doc({
				"doctype": "Notification Log",
				"for_user": user,
				"type": "Alert",
				"subject": title,
				"email_status": "Open",
				"notification_count": 0,
				"description": desc,
			}).insert(ignore_permissions=True)
		frappe.cache.set_value(dedup_key, 1, expires_in_sec=86400 * 2)
		reminded += 1
	frappe.db.commit()
	return reminded

