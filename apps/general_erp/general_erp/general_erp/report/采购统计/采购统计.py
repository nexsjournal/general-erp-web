# -*- coding: utf-8 -*-
import frappe
from frappe import _


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("from_date"):
		filters["from_date"] = frappe.utils.get_first_day(frappe.utils.nowdate())
	if not filters.get("to_date"):
		filters["to_date"] = frappe.utils.nowdate()
	group_map = {
		"月份": "DATE_FORMAT(po.transaction_date, '%%Y-%%m')",
		"供应商": "po.supplier",
		"商品": "CONCAT(poi.item_code, '|', poi.item_name)",
	}
	group_col = group_map[filters.get("group_by") or "月份"]
	supplier_filter = ""
	if filters.get("supplier"):
		supplier_filter = "AND po.supplier = %(supplier)s"
	sql = (
		"SELECT DATE_FORMAT(po.transaction_date, '%%Y-%%m') AS period, po.supplier, "
		"COALESCE(poi.item_code, '') AS item_code, COALESCE(poi.item_name, '') AS item_name, "
		"COALESCE(SUM(poi.qty), 0) AS qty, COALESCE(SUM(poi.base_amount), 0) AS amount "
		"FROM `tabPurchase Order` po JOIN `tabPurchase Order Item` poi ON poi.parent = po.name "
		"WHERE po.docstatus < 2 AND po.transaction_date BETWEEN %(from_date)s AND %(to_date)s " + supplier_filter + " "
		"GROUP BY " + group_col + ", po.supplier, poi.item_code, poi.item_name ORDER BY " + group_col
	)
	rows = frappe.db.sql(sql, {"from_date": filters["from_date"], "to_date": filters["to_date"], "supplier": filters.get("supplier")}, as_dict=True)
	data = []
	group = filters.get("group_by") or "月份"
	for r in rows:
		data.append({
			"period": r.period if group != "商品" else "",
			"supplier": r.supplier if group != "商品" else "",
			"item_code": r.item_code if group == "商品" else "",
			"item_name": r.item_name if group == "商品" else "",
			"qty": r.qty or 0,
			"amount": r.amount or 0,
		})
	columns = [
		{"label": _("期间"), "fieldname": "period", "fieldtype": "Data"},
		{"label": _("供应商"), "fieldname": "supplier", "fieldtype": "Data"},
		{"label": _("商品编码"), "fieldname": "item_code", "fieldtype": "Data"},
		{"label": _("商品名称"), "fieldname": "item_name", "fieldtype": "Data"},
		{"label": _("数量"), "fieldname": "qty", "fieldtype": "Float"},
		{"label": _("金额"), "fieldname": "amount", "fieldtype": "Currency"},
	]

	return columns, data
