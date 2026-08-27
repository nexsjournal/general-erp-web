# -*- coding: utf-8 -*-
import frappe
from frappe import _


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("from_date"):
		filters["from_date"] = frappe.utils.add_years(frappe.utils.nowdate(), -1)
	if not filters.get("to_date"):
		filters["to_date"] = frappe.utils.nowdate()
	period_expr = "DATE_FORMAT(COALESCE(s.etd, DATE(s.creation)), '%%Y-%%m')"
	group_col = {
		"月份": period_expr,
		"目的港": "s.port_of_discharge",
		"客户": "s.customer",
	}[filters.get("group_by") or "月份"]
	customer_filter = "AND s.customer = %(customer)s" if filters.get("customer") else ""
	sql = (
		"SELECT " + period_expr + " AS period, s.customer AS customer, "
		"p.port_name AS port_of_discharge, i.chinese_name AS incoterms, "
		"s.transport_mode AS transport_mode, COUNT(DISTINCT s.name) AS shipment_count, "
		"COALESCE(SUM(si.qty), 0) AS qty, COALESCE(SUM(si.gross_weight), 0) AS gross_weight, "
		"COALESCE(SUM(si.volume), 0) AS volume "
		"FROM `tabShipment` s LEFT JOIN `tabShipment Item` si ON si.parent = s.name "
	"LEFT JOIN `tabPort` p ON p.name = s.port_of_discharge "
	"LEFT JOIN `tabIncoterms` i ON i.name = s.incoterms "
		"WHERE DATE(COALESCE(s.etd, s.creation)) BETWEEN %(from_date)s AND %(to_date)s " + customer_filter + " "
		"GROUP BY " + group_col + " ORDER BY " + group_col
	)
	rows = frappe.db.sql(
		sql,
		{"from_date": filters["from_date"], "to_date": filters["to_date"], "customer": filters.get("customer")},
		as_dict=True,
	)
	group = filters.get("group_by") or "月份"
	data = []
	for r in rows:
		data.append({
			"period": r.period,
			"customer": r.customer if group == "客户" else "",
			"port_of_discharge": r.port_of_discharge if group == "目的港" else "",
			"incoterms": r.incoterms or "",
			"transport_mode": r.transport_mode or "",
			"shipment_count": r.shipment_count,
			"qty": r.qty or 0,
			"gross_weight": r.gross_weight or 0,
			"volume": r.volume or 0,
		})
	columns = [
		{"label": _("期间"), "fieldname": "period", "fieldtype": "Data"},
		{"label": _("客户"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer"},
		{"label": _("目的港"), "fieldname": "port_of_discharge", "fieldtype": "Link", "options": "Port"},
		{"label": _("贸易术语"), "fieldname": "incoterms", "fieldtype": "Data"},
		{"label": _("运输方式"), "fieldname": "transport_mode", "fieldtype": "Data"},
		{"label": _("出运单数"), "fieldname": "shipment_count", "fieldtype": "Int"},
		{"label": _("数量"), "fieldname": "qty", "fieldtype": "Float"},
		{"label": _("毛重(KG)"), "fieldname": "gross_weight", "fieldtype": "Float"},
		{"label": _("体积(CBM)"), "fieldname": "volume", "fieldtype": "Float"},
	]
	return columns, data
