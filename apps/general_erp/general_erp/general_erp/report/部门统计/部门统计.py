# -*- coding: utf-8 -*-
import frappe
from frappe import _


def execute(filters=None):
	from general_erp.general_erp.report_utils import check_report_access
	check_report_access("部门统计")
	"""部门统计：各部门人数、关联客户数（按销售负责人归属）、跟进数。"""
	rows = frappe.db.sql(
		"SELECT de.name AS department, de.department_name AS dept_name, "
		"count(DISTINCT e.name) AS headcount, "
		"count(DISTINCT c.name) AS customers, "
		"count(DISTINCT f.name) AS follows "
		"FROM `tabDepartment` de "
		"LEFT JOIN `tabEmployee` e ON e.department = de.name "
		"LEFT JOIN `tabUser` u ON u.name = e.user_id "
		"LEFT JOIN `tabCustomer` c ON c.sales_owner = u.name "
		"LEFT JOIN `tabCustomer Follow Up` f ON f.customer = c.name "
		"GROUP BY de.name, de.department_name ORDER BY headcount DESC, customers DESC", as_dict=True)
	data = [{
		"department": r.department, "dept_name": r.dept_name or "",
		"headcount": r.headcount, "customers": r.customers or 0, "follows": r.follows or 0,
	} for r in rows if r.headcount or r.customers]
	columns = [
		{"label": _("部门"), "fieldname": "department", "fieldtype": "Link", "options": "Department"},
		{"label": _("部门名称"), "fieldname": "dept_name", "fieldtype": "Data"},
		{"label": _("人数"), "fieldname": "headcount", "fieldtype": "Int"},
		{"label": _("客户数"), "fieldname": "customers", "fieldtype": "Int"},
		{"label": _("跟进数"), "fieldname": "follows", "fieldtype": "Int"},
	]
	return columns, data
