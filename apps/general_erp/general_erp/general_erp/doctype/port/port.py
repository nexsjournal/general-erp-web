import frappe

from frappe.model.document import Document


class Port(Document):
	"""港口：外贸装运港/目的港主数据，报价单与销售订单引用。"""
