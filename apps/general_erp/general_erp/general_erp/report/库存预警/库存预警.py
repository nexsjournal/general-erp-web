# -*- coding: utf-8 -*-
import frappe
from frappe import _


def execute(filters=None):
	from general_erp.general_erp.report_utils import check_report_access
	check_report_access("库存预警")
	"""可用库存低于再订货点的物料（按仓库维度），用于库存预警。"""
	sql = (
	"SELECT i.item_code, i.item_name, COALESCE(b.warehouse, '') AS warehouse, "
		"COALESCE(b.projected_qty, 0) AS projected_qty, "
		"i.safety_stock, (i.safety_stock - COALESCE(b.projected_qty, 0)) AS shortage "
	"FROM `tabItem` i LEFT JOIN `tabBin` b ON b.item_code = i.name "
		"WHERE i.safety_stock > 0 AND COALESCE(b.projected_qty, 0) < i.safety_stock "
		"AND i.disabled = 0 "
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
