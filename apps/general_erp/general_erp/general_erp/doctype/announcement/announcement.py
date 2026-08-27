import frappe

from frappe.model.document import Document


class Announcement(Document):
	"""通知公告：公司级公告，支持置顶与有效期。"""
