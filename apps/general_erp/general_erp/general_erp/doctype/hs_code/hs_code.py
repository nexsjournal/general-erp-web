import frappe

from frappe.model.document import Document


class HSCode(Document):
	"""海关商品编码（HS Code）库：关联商品，供出口报关与单证使用。"""
