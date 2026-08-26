import frappe

from frappe.model.document import Document


class SystemParameter(Document):
	"""系统参数：公海回收、跟进提醒等全局开关与阈值。"""
