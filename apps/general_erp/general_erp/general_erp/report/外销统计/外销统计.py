# -*- coding: utf-8 -*-
import frappe
from frappe import _


def execute(filters=None):
	from general_erp.general_erp.report_utils import check_report_access
	check_report_access("外销统计")
	filters = frappe._dict(filters or {})
	if not filters.get("from_date"):
		filters["from_date"] = frappe.utils.get_first_day(frappe.utils.nowdate())
	if not filters.get("to_date"):
		filters["to_date"] = frappe.utils.nowdate()
	group_col = {
		"月份": "DATE_FORMAT(so.transaction_date, '%%Y-%%m')",
		"业务员": "so.owner",
		"客户": "so.customer",
	}[filters.get("group_by") or "月份"]
	owner_filter = ""
	if filters.get("salesperson"):
		owner_filter = "AND so.owner = %(salesperson)s"
	sql = (
		"SELECT DATE_FORMAT(so.transaction_date, '%%Y-%%m') AS period, so.owner, so.customer AS customer, "
		"COUNT(DISTINCT so.name) AS order_count, "
		"COALESCE(SUM(si.subtotal_qty), 0) AS qty, "
		"SUM(so.base_grand_total) AS amount "
		"FROM `tabSales Order` so "
		"LEFT JOIN (SELECT parent, SUM(qty) AS subtotal_qty FROM `tabSales Order Item` GROUP BY parent) si ON si.parent = so.name "
		"WHERE so.docstatus = 1 "
		"AND so.transaction_date BETWEEN %(from_date)s AND %(to_date)s " + owner_filter + " "
		"GROUP BY " + group_col + " ORDER BY " + group_col
	)
	rows = frappe.db.sql(sql, {"from_date": filters["from_date"], "to_date": filters["to_date"], "salesperson": filters.get("salesperson")}, as_dict=True)
	data = []
	group = filters.get("group_by") or "月份"
	for r in rows:
		data.append({
			"period": r.period,
			"owner": r.owner if group == "业务员" else "",
			"customer": r.customer if group == "客户" else "",
			"order_count": r.order_count,
			"qty": r.qty or 0,
			"amount": r.amount or 0,
		})
	columns = [
		{"label": _("期间"), "fieldname": "period", "fieldtype": "Data"},
		{"label": _("业务员"), "fieldname": "owner", "fieldtype": "Data"},
		{"label": _("客户"), "fieldname": "customer", "fieldtype": "Data"},
		{"label": _("订单数"), "fieldname": "order_count", "fieldtype": "Int"},
		{"label": _("数量"), "fieldname": "qty", "fieldtype": "Float"},
		{"label": _("金额"), "fieldname": "amount", "fieldtype": "Currency"},
	]

	return columns, data
