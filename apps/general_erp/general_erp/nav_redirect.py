# -*- coding: utf-8 -*-
"""T-nav-fix: 登录落地导航统一（金蝶式两级首页，非侵入）

- 已登录访问根地址 /  -> /desk/首页（frappe 官方 home_page 钩子链路）
- 已登录访问 /desk 裸路由 -> /desk/首页（website_redirects 钩子链路）
- 未登录一律不重定向（仍走登录页）；/desk/xxx 子路由不受影响
"""
import frappe


def get_home_page(user):
	# 仅已登录用户；guest 返回 None 走 frappe 默认（登录页/404）
	if user and user != "Guest":
		return "/desk/%E9%A6%96%E9%A1%B5"
	return None


def website_redirect(path):
	# 只处理 /desk 裸路由；返回 None = 不重定向
	if path == "desk":
		user = getattr(frappe.session, "user", None)
		if user and user != "Guest":
			return "/desk/%E9%A6%96%E9%A1%B5"
	return None
