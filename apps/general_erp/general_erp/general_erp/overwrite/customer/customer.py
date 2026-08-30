# -*- coding: utf-8 -*-
"""Customer 权限覆盖：User Permission 数据隔离加固（P1-1）。

frappe 的 User Permission 只拦列表/链接选择，不拦 by-name 直读（get_doc / URL 直达）。
这里在 has_permission 层补一道：普通销售只能访问 User Permission 内的客户；
Sales Manager / System Manager / Administrator 不受限。

关键：User Permission 隔离只作用于【已存在】的客户（读取场景）。新建客户时
doc.name 尚未落库，必须走纯角色级权限检查（不传 doc，否则 frappe 会按
name=None 查不到 User Permission 而拒绝，导致销售建不了新客户）。
"""
import frappe
from frappe.permissions import has_permission
from erpnext.selling.doctype.customer.customer import Customer as _BaseCustomer


class Customer(_BaseCustomer):
	def has_permission(self, ptype=None, verbose=False):
		user = frappe.session.user
		if user == "Administrator":
			return super().has_permission(ptype)

		# 新建客户（name 尚未落库）：走纯角色级权限（不传 doc，不查 User Permission），
		# 否则销售会因为查不到 User Permission 而无法创建新客户。
		if not self.get("name") or not frappe.db.exists("Customer", self.name):
			return has_permission("Customer", ptype or "read", user=user)

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
