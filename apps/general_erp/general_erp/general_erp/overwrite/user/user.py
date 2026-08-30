# -*- coding: utf-8 -*-
"""User 覆盖：支持无邮箱账号（T-user-login，2026-08-29）。

国内习惯：管理员建号只给用户名+密码，邮箱可不填。
frappe 原生以 email 为身份锚点（autoname: name=email，validate 强制 email=name 且格式校验）。
本覆盖非侵入地放开：
  - 有邮箱：行为与原生完全一致（name=email）
  - 无邮箱：name 取 username，跳过邮箱强制；登录走 System Settings
    allow_login_using_user_name（frappe 原生开关，after_migrate 幂等开启）
覆盖体复制自 frappe v16 user.py 的 autoname/validate，仅加无邮箱分支；
frappe 升级后需 diff 同步本文件（与 overwrite/customer 同一维护约定）。
"""
import frappe
from frappe.core.doctype.user.user import User as _BaseUser, STANDARD_USERS


class User(_BaseUser):
	def autoname(self):
		"""set name as Email Address（无邮箱时取 username）"""
		if self.get("is_admin") or self.get("is_guest"):
			self.name = self.first_name
		elif self.email:
			self.email = self.email.strip().lower()
			self.name = self.email
		elif self.username:
			self.name = self.username
		else:
			frappe.throw(frappe._("邮箱和用户名至少填一项"))

	def validate(self):
		# 无邮箱账号：用 username 兜底 first_name（frappe first_name 必填）
		if not self.first_name and self.username:
			self.first_name = self.username

		if self.new_password:
			self._User__new_password = self.new_password
			self.new_password = ""

		if not frappe.in_test:
			self.password_strength_test()

		if self.name not in STANDARD_USERS:
			if self.email:
				self.email = self.name if self.email == self.name else self.email
				self.validate_email_type(self.email)
			# 无邮箱分支：不做 email=name 同步与格式校验

		self.move_role_profile_name_to_role_profiles()
		self.populate_role_profile_roles()
		self.check_roles_added()
		self.set_system_user()
		self.clean_name()
		self.set_full_name()
		self.check_enable_disable()
		self.ensure_unique_roles()
		self.ensure_unique_role_profiles()
		self.sync_role_profile_name()
		self.remove_all_roles_for_guest()
		self.validate_username()
		self.remove_disabled_roles()
		if self.email:
			self.validate_user_email_inbox()
		if self.user_emails:
			from frappe.utils.password import ask_pass_update
			ask_pass_update()
		self.validate_allowed_modules()
		self.validate_user_image()
		self.set_time_zone()
		if self.restrict_ip:
			self.validate_ip_addr()

		if self.language == "Loading...":
			self.language = None

		if self.default_app and self.default_app not in frappe.get_installed_apps():
			self.default_app = ""

		if (self.name not in ["Administrator", "Guest"]) and (not self.get_social_login_userid("frappe")):
			self.set_social_login_userid("frappe", frappe.generate_hash(length=39))
