import frappe

from frappe.model.document import Document


class ServiceProvider(Document):
	"""服务商：货代、船公司、检验机构、报关行等外贸服务商档案。"""
