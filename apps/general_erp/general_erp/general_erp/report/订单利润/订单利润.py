# -*- coding: utf-8 -*-
import frappe
from frappe import _


def execute(filters=None):
	from general_erp.general_erp.report_utils import check_report_access
	check_report_access("订单利润")
	filters = frappe._dict(filters or {})
	if not filters.get("from_date"):
		filters["from_date"] = frappe.utils.get_first_day(frappe.utils.nowdate())
	if not filters.get("to_date"):
		filters["to_date"] = frappe.utils.nowdate()
	customer_filter = ""
	if filters.get("customer"):
		customer_filter = "AND so.customer = %(customer)s"
	sql = (
		"SELECT so.name, so.transaction_date, so.customer AS customer, so.base_grand_total AS revenue, "
		"(SELECT COALESCE(SUM(sii.valuation_rate * sii.qty), 0) FROM `tabSales Order Item` sii WHERE sii.parent = so.name) AS cost, "
		"(SELECT COALESCE(SUM(e.amount), 0) FROM `tabExpense Reimbursement` e WHERE e.sales_order = so.name AND e.docstatus = 1) AS expenses "
		"FROM `tabSales Order` so WHERE so.docstatus = 1 "
		"AND so.transaction_date BETWEEN %(from_date)s AND %(to_date)s " + customer_filter + " "
		"ORDER BY so.transaction_date"
	)
	rows = frappe.db.sql(sql, {"from_date": filters["from_date"], "to_date": filters["to_date"], "customer": filters.get("customer")}, as_dict=True)
	data = []
	for r in rows:
		revenue = r.revenue or 0
		cost = r.cost or 0
		expenses = r.expenses or 0
		profit = revenue - cost - expenses
		margin = round(profit / revenue * 100, 2) if revenue else 0
		data.append({
			"name": r.name,
			"customer": r.customer,
			"date": frappe.utils.formatdate(r.transaction_date, "yyyy-MM-dd"),
			"revenue": revenue,
			"cost": cost,
			"expenses": expenses,
			"profit": profit,
			"margin": margin,
		})
	columns = [
		{"label": _("订单"), "fieldname": "name", "fieldtype": "Link", "options": "Sales Order"},
		{"label": _("客户"), "fieldname": "customer", "fieldtype": "Data"},
		{"label": _("日期"), "fieldname": "date", "fieldtype": "Data"},
		{"label": _("收入"), "fieldname": "revenue", "fieldtype": "Currency"},
		{"label": _("成本"), "fieldname": "cost", "fieldtype": "Currency"},
		{"label": _("费用"), "fieldname": "expenses", "fieldtype": "Currency"},
		{"label": _("毛利"), "fieldname": "profit", "fieldtype": "Currency"},
		{"label": _("毛利率 %"), "fieldname": "margin", "fieldtype": "Float"},
	]

	return columns, data
