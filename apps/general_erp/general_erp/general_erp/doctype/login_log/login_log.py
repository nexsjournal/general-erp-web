import frappe

from frappe.model.document import Document


class LoginLog(Document):
	"""登录日志：记录用户登录/登出（由 hooks.py 的 on_login / on_logout 钩子写入，只增不改）。"""


def _record(event):
	"""写入一条登录日志；失败只记 error log，绝不影响登录/登出主流程。"""
	try:
		user = frappe.session.user
		if not user or user == "Guest":
			return
		request = getattr(frappe.local, "request", None)
		agent = ""
		if request is not None:
			agent = request.headers.get("User-Agent", "")
		doc = frappe.new_doc("Login Log")
		doc.update(
			{
				"event": event,
				"user": user,
				"full_name": frappe.db.get_value("User", user, "full_name", cache=True),
				"ip_address": getattr(frappe.local, "request_ip", "") or "",
				"user_agent": agent[:500],
				"login_time": frappe.utils.now_datetime(),
			}
		)
		doc.flags.ignore_permissions = True
		doc.insert(ignore_if_duplicate=True)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Login Log 写入失败")


def on_login(login_manager):
	"""on_login 钩子：密码/OTP 登录成功后触发（会话续期不触发，不会刷屏）。"""
	_record("登录")


def on_logout(login_manager):
	"""on_logout 钩子：用户主动登出时触发。"""
	_record("登出")
