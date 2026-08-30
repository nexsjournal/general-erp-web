# -*- coding: utf-8 -*-
import frappe
from frappe import _


def execute(filters=None):
	from general_erp.general_erp.report_utils import check_report_access
	check_report_access("出运日志")
	"""出运日志：全部出运单的状态轨迹 + 关联沟通记录（出运事件流水）。"""
	rows = frappe.db.sql(
		"SELECT s.name, s.customer, s.bl_no, s.container_no, s.etd, s.eta, s.status, "
		"s.transport_mode, s.vessel_voyage, s.modified, s.modified_by, "
		"c.content AS last_comment "
		"FROM `tabExport Shipment` s "
		"LEFT JOIN `tabCommunication` c ON c.reference_doctype = 'Export Shipment' "
		"AND c.reference_name = s.name AND c.name = ("
		"  SELECT name FROM `tabCommunication` cc WHERE cc.reference_doctype = 'Export Shipment' "
		"  AND cc.reference_name = s.name ORDER BY cc.creation DESC LIMIT 1) "
		"ORDER BY s.creation DESC", as_dict=True)
	data = [{
		"name": r.name, "customer": r.customer or "", "bl_no": r.bl_no or "",
		"container_no": r.container_no or "", "etd": str(r.etd or ""), "eta": str(r.eta or ""),
		"status": r.status or "", "transport_mode": r.transport_mode or "",
		"vessel_voyage": r.vessel_voyage or "",
		"last_comment": (r.last_comment or "").replace(chr(10), " ")[:80],
		"updated": str(r.modified or "")[:16], "updated_by": r.modified_by or "",
	} for r in rows]
	columns = [
		{"label": _("出运单"), "fieldname": "name", "fieldtype": "Link", "options": "Export Shipment"},
		{"label": _("客户"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer"},
		{"label": _("提单号"), "fieldname": "bl_no", "fieldtype": "Data"},
		{"label": _("柜号"), "fieldname": "container_no", "fieldtype": "Data"},
		{"label": _("ETD"), "fieldname": "etd", "fieldtype": "Data"},
		{"label": _("ETA"), "fieldname": "eta", "fieldtype": "Data"},
		{"label": _("状态"), "fieldname": "status", "fieldtype": "Data"},
		{"label": _("运输方式"), "fieldname": "transport_mode", "fieldtype": "Data"},
		{"label": _("船名航次"), "fieldname": "vessel_voyage", "fieldtype": "Data"},
		{"label": _("最新记录"), "fieldname": "last_comment", "fieldtype": "Data"},
		{"label": _("更新时间"), "fieldname": "updated", "fieldtype": "Data"},
		{"label": _("操作人"), "fieldname": "updated_by", "fieldtype": "Data"},
	]
	return columns, data
