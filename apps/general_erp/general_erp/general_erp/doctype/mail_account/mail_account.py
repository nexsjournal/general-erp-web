import frappe

from frappe.model.document import Document


class MailAccount(Document):
	"""邮箱账号：员工 IMAP/SMTP 邮箱配置，密码加密存储。"""
