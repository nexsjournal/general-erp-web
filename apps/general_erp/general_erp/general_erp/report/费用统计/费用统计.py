# -*- coding: utf-8 -*-
import frappe
from frappe import _


def execute(filters=None):
	from general_erp.general_erp.report_utils import check_report_access
	check_report_access("费用统计")
	filters = frappe._dict(filters or {})
	if not filters.get("from_date"):
		filters["from_date"] = frappe.utils.get_first_day(frappe.utils.nowdate())
	if not filters.get("to_date"):
		filters["to_date"] = frappe.utils.nowdate()
	group_col = {
		"月份": "DATE_FORMAT(e.expense_date, '%%Y-%%m')",
		"费用类型": "e.expense_type",
		"申请人": "e.applicant",
	}[filters.get("group_by") or "月份"]
	sql = (
		"SELECT DATE_FORMAT(e.expense_date, '%%Y-%%m') AS period, e.expense_type, e.applicant, "
		"COUNT(*) AS entry_count, SUM(e.amount) AS amount "
		"FROM `tabExpense Reimbursement` e WHERE e.docstatus = 1 "
		"AND e.expense_date BETWEEN %(from_date)s AND %(to_date)s "
		"GROUP BY " + group_col + " ORDER BY " + group_col
	)
	rows = frappe.db.sql(sql, {"from_date": filters["from_date"], "to_date": filters["to_date"]}, as_dict=True)
	data = []
	group = filters.get("group_by") or "月份"
	for r in rows:
		data.append({
			"period": r.period if group != "费用类型" else "",
			"expense_type": r.expense_type if group == "费用类型" else "",
			"applicant": r.applicant if group == "申请人" else "",
			"entry_count": r.entry_count,
			"amount": r.amount or 0,
		})
	columns = [
		{"label": _("期间"), "fieldname": "period", "fieldtype": "Data"},
		{"label": _("费用类型"), "fieldname": "expense_type", "fieldtype": "Data"},
		{"label": _("申请人"), "fieldname": "applicant", "fieldtype": "Data"},
		{"label": _("笔数"), "fieldname": "entry_count", "fieldtype": "Int"},
		{"label": _("金额"), "fieldname": "amount", "fieldtype": "Currency"},
	]

	return columns, data
