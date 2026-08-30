# -*- coding: utf-8 -*-
import frappe
from frappe import _


def execute(filters=None):
	from general_erp.general_erp.report_utils import check_report_access
	check_report_access("订单条目")
	"""订单条目：销售订单明细行流水（商品级数量/单价/金额/已交货进度）。"""
	rows = frappe.db.sql(
		"SELECT soi.parent AS sales_order, s.customer, soi.item_code, i.item_name AS item_name, "
		"soi.qty, soi.rate, soi.amount, coalesce(soi.delivered_qty, 0) AS delivered_qty, "
		"s.status AS so_status, s.transaction_date "
		"FROM `tabSales Order Item` soi "
		"JOIN `tabSales Order` s ON s.name = soi.parent "
		"LEFT JOIN `tabItem` i ON i.name = soi.item_code "
		"WHERE s.docstatus = 1 ORDER BY s.creation DESC, soi.idx", as_dict=True)
	data = [{
		"sales_order": r.sales_order, "customer": r.customer or "",
		"item_code": r.item_code or "", "item_name": r.item_name or "",
		"qty": r.qty or 0, "rate": r.rate or 0, "amount": r.amount or 0,
		"delivered_qty": r.delivered_qty or 0,
		"progress": str(round((r.delivered_qty or 0) * 100.0 / r.qty, 0)) + "%" if r.qty else "-",
		"so_status": r.so_status or "", "transaction_date": str(r.transaction_date or ""),
	} for r in rows]
	columns = [
		{"label": _("销售订单"), "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order"},
		{"label": _("客户"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer"},
		{"label": _("商品编码"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item"},
		{"label": _("商品名称"), "fieldname": "item_name", "fieldtype": "Data"},
		{"label": _("数量"), "fieldname": "qty", "fieldtype": "Float"},
		{"label": _("单价"), "fieldname": "rate", "fieldtype": "Currency"},
		{"label": _("金额"), "fieldname": "amount", "fieldtype": "Currency"},
		{"label": _("已交货"), "fieldname": "delivered_qty", "fieldtype": "Float"},
		{"label": _("交货进度"), "fieldname": "progress", "fieldtype": "Data"},
		{"label": _("订单状态"), "fieldname": "so_status", "fieldtype": "Data"},
		{"label": _("订单日期"), "fieldname": "transaction_date", "fieldtype": "Data"},
	]
	return columns, data
