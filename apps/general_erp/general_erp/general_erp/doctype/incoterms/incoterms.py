import frappe

from frappe.model.document import Document


class Incoterms(Document):
	"""贸易术语（Incoterms 2020）：报价单与销售订单引用。"""
