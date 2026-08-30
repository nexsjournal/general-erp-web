# -*- coding: utf-8 -*-
import frappe
from frappe import _


def execute(filters=None):
	from general_erp.general_erp.report_utils import check_report_access
	check_report_access("员工工作情况表")
	from frappe.utils import nowdate
	filters = frappe._dict(filters or {})
	month_start = nowdate()[:8] + "01"
	from_date = filters.get("from_date") or month_start
	to_date = filters.get("to_date") or nowdate()

	users = frappe.get_all("User", filters={"enabled": 1, "user_type": "System User"}, fields=["name", "full_name"])
	# 批量 SQL（T2-20 去 N+1）：单条查询覆盖全部用户
	batch_sql = (
		"SELECT u.name AS user, u.full_name, "
		"(SELECT COUNT(*) FROM `tabCustomer Follow Up` f WHERE f.followed_by = u.name AND f.follow_date BETWEEN %(fd)s AND %(td)s) AS follows, "
		"(SELECT COUNT(*) FROM `tabMail` m WHERE m.sender = u.name AND m.folder = '已发送' AND m.sent_at BETWEEN %(fd)s AND %(td)s) AS mail_out, "
		"(SELECT COUNT(*) FROM `tabMail` m WHERE m.sender = u.name AND m.folder = '收件箱' AND m.sent_at BETWEEN %(fd)s AND %(td)s) AS mail_in, "
		"(SELECT COUNT(*) FROM `tabQuotation` q WHERE q.owner = u.name AND q.creation BETWEEN %(fd)s AND %(td)s) AS quotations, "
		"(SELECT COUNT(*) FROM `tabOpportunity` o WHERE o.opportunity_owner = u.name AND o.creation BETWEEN %(fd)s AND %(td)s) AS new_opps, "
		"(SELECT COALESCE(SUM(o.opportunity_amount), 0) FROM `tabOpportunity` o WHERE o.opportunity_owner = u.name AND o.creation BETWEEN %(fd)s AND %(td)s) AS opp_amount, "
		"(SELECT COUNT(*) FROM `tabWork Check` wc JOIN `tabWork Check Item` it ON it.parent = wc.name WHERE wc.assignee = u.name AND wc.check_date BETWEEN %(fd)s AND %(td)s AND it.done = 1) AS done_items "
		"FROM `tabUser` u WHERE u.enabled = 1 AND u.user_type = 'System User'"
	)
	batch = frappe.db.sql(batch_sql, {"fd": from_date, "td": to_date}, as_dict=True)
	rows = []
	for b in batch:
		if b.follows or b.mail_out or b.mail_in or b.quotations or b.opp_amount or b.done_items:
			rows.append({
				"employee": b.full_name or b.user,
				"follows": b.follows,
				"mail_out": b.mail_out,
				"mail_in": b.mail_in,
				"quotations": b.quotations,
				"new_opps": b.new_opps,
				"opp_amount": b.opp_amount,
				"check_items_done": b.done_items,
			})
	columns = [
		{"label": _("员工"), "fieldname": "employee", "fieldtype": "Data"},
		{"label": _("跟进数"), "fieldname": "follows", "fieldtype": "Int"},
		{"label": _("发出邮件"), "fieldname": "mail_out", "fieldtype": "Int"},
		{"label": _("收到邮件"), "fieldname": "mail_in", "fieldtype": "Int"},
		{"label": _("报价数"), "fieldname": "quotations", "fieldtype": "Int"},
		{"label": _("新商机"), "fieldname": "new_opps", "fieldtype": "Int"},
		{"label": _("商机金额"), "fieldname": "opp_amount", "fieldtype": "Currency"},
		{"label": _("完成检查项"), "fieldname": "check_items_done", "fieldtype": "Int"},
	]
	return columns, rows
