# -*- coding: utf-8 -*-
import frappe
from frappe import _


def execute(
filters=None):
	from general_erp.general_erp.report_utils import check_report_access
	check_report_access("产品统计")
	filters = frappe._dict(filters or {})
	if not filters.get("from_date"):
		filters["from_date"] = frappe.utils.get_first_day(frappe.utils.nowdate())
	if not filters.get("to_date"):
		filters["to_date"] = frappe.utils.nowdate()
	group_map = {
		"月份": "DATE_FORMAT(si.posting_date, '%%Y-%%m')",
		"商品": "CONCAT(sii.item_code, '|', sii.item_name)",
	}
	group_col = group_map[filters.get("group_by") or "月份"]
	item_filter = ""
	if filters.get("item"):
		item_filter = "AND sii.item_code = %(item)s"
	sql = (
		"SELECT DATE_FORMAT(si.posting_date, '%%Y-%%m') AS period, "
		"COALESCE(sii.item_code, '') AS item_code, COALESCE(sii.item_name, '') AS item_name, "
		"COALESCE(SUM(sii.qty), 0) AS qty, COALESCE(SUM(sii.base_amount), 0) AS amount "
		"FROM `tabSales Invoice` si JOIN `tabSales Invoice Item` sii ON sii.parent = si.name "
		"WHERE si.docstatus = 1 AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s " + item_filter + " "
		"GROUP BY " + group_col + ", sii.item_code, sii.item_name ORDER BY " + group_col
	)
	rows = frappe.db.sql(sql, {"from_date": filters["from_date"], "to_date": filters["to_date"], "item": filters.get("item")}, as_dict=True)
	data = []
	group = filters.get("group_by") or "月份"
	for r in rows:
		data.append({
			"period": r.period if group != "商品" else "",
			"item_code": r.item_code if group == "商品" else "",
			"item_name": r.item_name if group == "商品" else "",
			"qty": r.qty or 0,
			"amount": r.amount or 0,
		})
	columns = [
		{"label": _("期间"), "fieldname": "period", "fieldtype": "Data"},
		{"label": _("商品编码"), "fieldname": "item_code", "fieldtype": "Data"},
		{"label": _("商品名称"), "fieldname": "item_name", "fieldtype": "Data"},
		{"label": _("数量"), "fieldname": "qty", "fieldtype": "Float"},
		{"label": _("金额"), "fieldname": "amount", "fieldtype": "Currency"},
	]

	return columns, data
