# -*- coding: utf-8 -*-
import frappe
from frappe import _


def execute(filters=None):
	"""可用库存低于再订货点的物料（按仓库维度），用于库存预警。"""
	sql = (
		"SELECT i.item_code, i.item_name, b.warehouse, b.projected_qty, "
		"i.reorder_level, (i.reorder_level - b.projected_qty) AS shortage "
		"FROM `tabBin` b JOIN `tabItem` i ON i.name = b.item_code "
		"WHERE i.reorder_level > 0 AND b.projected_qty < i.reorder_level "
		"ORDER BY shortage DESC"
	)
	rows = frappe.db.sql(sql, as_dict=True)
	columns = [
		{"label": _("物料"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item"},
		{"label": _("物料名称"), "fieldname": "item_name", "fieldtype": "Data"},
		{"label": _("仓库"), "fieldname": "warehouse", "fieldtype": "Data"},
		{"label": _("可用库存"), "fieldname": "projected_qty", "fieldtype": "Float"},
		{"label": _("再订货点"), "fieldname": "reorder_level", "fieldtype": "Float"},
		{"label": _("缺口"), "fieldname": "shortage", "fieldtype": "Float"},
	]
	return columns, rows
