# -*- coding: utf-8 -*-
import frappe
from frappe import _


def execute(filters=None):
	from general_erp.general_erp.report_utils import check_report_access
	check_report_access("员工统计")
	"""员工统计：按部门/岗位/在职状态汇总人数。"""
	rows = frappe.db.sql(
		"SELECT coalesce(de.department_name, '（未分配）') AS department, "
		"coalesce(e.designation, '（未分配）') AS designation, e.status, count(*) AS headcount "
		"FROM `tabEmployee` e LEFT JOIN `tabDepartment` de ON de.name = e.department "
		"GROUP BY de.department_name, e.designation, e.status ORDER BY headcount DESC", as_dict=True)
	data = [{
		"department": r.department, "designation": r.designation or "",
		"status": r.status or "", "headcount": r.headcount,
	} for r in rows]
	columns = [
		{"label": _("部门"), "fieldname": "department", "fieldtype": "Data"},
		{"label": _("岗位"), "fieldname": "designation", "fieldtype": "Data"},
		{"label": _("状态"), "fieldname": "status", "fieldtype": "Data"},
		{"label": _("人数"), "fieldname": "headcount", "fieldtype": "Int"},
	]
	return columns, data
