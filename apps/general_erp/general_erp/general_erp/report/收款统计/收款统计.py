# -*- coding: utf-8 -*-
import frappe
from frappe import _


def execute(filters=None):
	from general_erp.general_erp.report_utils import check_report_access
	check_report_access("收款统计")
	filters = frappe._dict(filters or {})
	if not filters.get("from_date"):
		filters["from_date"] = frappe.utils.get_first_day(frappe.utils.nowdate())
	if not filters.get("to_date"):
		filters["to_date"] = frappe.utils.nowdate()
	group_col = {
		"月份": "DATE_FORMAT(pe.posting_date, '%%Y-%%m')",
		"客户": "pe.party_name",
		"制单人": "pe.owner",
	}[filters.get("group_by") or "月份"]
	customer_filter = ""
	if filters.get("customer"):
		customer_filter = "AND pe.party_name = %(customer)s"
	sql = (
		"SELECT DATE_FORMAT(pe.posting_date, '%%Y-%%m') AS period, pe.party_name AS customer, pe.owner, "
		"COUNT(*) AS entry_count, SUM(pe.base_paid_amount) AS amount "
		"FROM `tabPayment Entry` pe WHERE pe.docstatus = 1 AND pe.payment_type = 'Receive' "
		"AND pe.posting_date BETWEEN %(from_date)s AND %(to_date)s " + customer_filter + " "
		"GROUP BY " + group_col + " ORDER BY " + group_col
	)
	rows = frappe.db.sql(sql, {"from_date": filters["from_date"], "to_date": filters["to_date"], "customer": filters.get("customer")}, as_dict=True)
	data = []
	group = filters.get("group_by") or "月份"
	for r in rows:
		data.append({
			"period": r.period,
			"customer": r.customer if group == "客户" else "",
			"owner": r.owner if group == "制单人" else "",
			"entry_count": r.entry_count,
			"amount": r.amount or 0,
		})
	columns = [
		{"label": _("期间"), "fieldname": "period", "fieldtype": "Data"},
		{"label": _("客户"), "fieldname": "customer", "fieldtype": "Data"},
		{"label": _("制单人"), "fieldname": "owner", "fieldtype": "Data"},
		{"label": _("笔数"), "fieldname": "entry_count", "fieldtype": "Int"},
		{"label": _("金额"), "fieldname": "amount", "fieldtype": "Currency"},
	]

	return columns, data
