import frappe

from frappe.model.document import Document


class ReportSubscription(Document):
	"""报表订阅行：报表 + 收件人 + 频率。"""
