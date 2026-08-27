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
	rows = []
	for u in users:
		fu = frappe.db.count("Customer Follow Up", {"followed_by": u.name, "follow_date": ["between", (from_date, to_date)]})
		mail_out = frappe.db.count("Mail", {"sender": u.name, "folder": "已发送", "sent_at": ["between", (from_date, to_date)]})
		mail_in = frappe.db.count("Mail", {"sender": u.name, "folder": "收件箱", "sent_at": ["between", (from_date, to_date)]})
		qt = frappe.db.count("Quotation", {"owner": u.name, "creation": ["between", (from_date, to_date)]})
		opp = frappe.db.get_all("Opportunity", filters={"opportunity_owner": u.name, "creation": ["between", (from_date, to_date)]}, fields=[{"SUM": "opportunity_amount", "as": "amt"}], as_list=True)
		amt = opp[0][0] if opp and opp[0][0] else 0
		wc = frappe.db.sql(
			"select count(*) from `tabWork Check` wc join `tabWork Check Item` it on it.parent = wc.name "
			"where wc.assignee = %s and wc.check_date between %s and %s and it.done = 1",
			(u.name, from_date, to_date), as_list=True)
		done_items = wc[0][0] if wc else 0
		if fu or mail_out or mail_in or qt or amt or done_items:
			rows.append({
				"employee": u.full_name or u.name,
				"follows": fu,
				"mail_out": mail_out,
				"mail_in": mail_in,
				"quotations": qt,
				"new_opps": frappe.db.count("Opportunity", {"opportunity_owner": u.name, "creation": ["between", (from_date, to_date)]}),
				"opp_amount": amt,
				"check_items_done": done_items,
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
