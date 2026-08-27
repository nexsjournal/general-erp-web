# -*- coding: utf-8 -*-
import frappe
from frappe import _


def execute(filters=None):
	from general_erp.general_erp.report_utils import check_report_access
	check_report_access("商机统计")
	"""商机按批复状态统计：数量、金额、赢单率。"""
	rows = frappe.db.sql(
		"SELECT coalesce(o.review_status, '（未设置）') AS stage, count(*) AS total, "
		"coalesce(sum(o.opportunity_amount), 0) AS amount, "
		"sum(case when o.status = 'Converted' then 1 else 0 end) AS converted "
		"FROM `tabOpportunity` o WHERE o.docstatus = 0 "
		"GROUP BY stage ORDER BY amount DESC", as_dict=True)
	data = []
	for r in rows:
		rate = round(r.converted * 100.0 / r.total, 1) if r.total else 0
		data.append({
			"stage": r.stage, "total": r.total, "amount": r.amount,
			"converted": r.converted or 0, "rate": str(rate) + "%",
		})
	columns = [
		{"label": _("批复状态"), "fieldname": "stage", "fieldtype": "Data"},
		{"label": _("商机数"), "fieldname": "total", "fieldtype": "Int"},
		{"label": _("商机金额"), "fieldname": "amount", "fieldtype": "Currency"},
		{"label": _("已成交"), "fieldname": "converted", "fieldtype": "Int"},
		{"label": _("赢单率"), "fieldname": "rate", "fieldtype": "Data"},
	]
	return columns, data
