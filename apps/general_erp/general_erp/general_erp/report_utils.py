# -*- coding: utf-8 -*-
"""报表访问控制：按「统计设置 → 报表角色」矩阵校验当前用户是否可见指定报表。"""
import frappe

from frappe import _


def check_report_access(report_name):
	"""矩阵未配置该报表时不限制；配置后仅 System Manager/Administrator 或命中角色可见。"""
	if frappe.session.user == "Administrator" or "System Manager" in frappe.get_roles():
		return
	matrix = frappe.get_all("Report Role", filters={"report": report_name}, fields=["role", "enabled"])
	if not matrix:
		return
	roles = set(frappe.get_roles())
	if not any(row.enabled and row.role in roles for row in matrix):
		frappe.throw(_("无权限查看该报表（报表角色限制）"), frappe.PermissionError)
