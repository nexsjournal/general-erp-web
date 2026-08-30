# -*- coding: utf-8 -*-
"""Customer 权限覆盖：User Permission 数据隔离加固（P1-1）。

frappe 的 User Permission 只拦列表/链接选择，不拦 by-name 直读（get_doc / URL 直达）。
这里在 has_permission 层补一道：普通销售只能访问 User Permission 内的客户；
Sales Manager / System Manager / Administrator 不受限。
"""
import frappe
from erpnext.selling.doctype.customer.customer import Customer as _BaseCustomer


class Customer(_BaseCustomer):
	def has_permission(self, ptype=None, verbose=False):
		user = frappe.session.user
		if user == "Administrator":
			return super().has_permission(ptype)
		roles = set(frappe.get_roles(user))
		# 管理角色不受隔离限制
		if roles & {"System Manager", "Sales Manager"}:
			return super().has_permission(ptype)
		# 普通销售：该客户必须在自己的 User Permission 内
		if frappe.db.exists("User Permission", {"user": user, "allow": "Customer", "for_value": self.name}):
			return super().has_permission(ptype)
		if verbose:
			frappe.throw(frappe._("无权查看该客户"), frappe.PermissionError)
		return False
