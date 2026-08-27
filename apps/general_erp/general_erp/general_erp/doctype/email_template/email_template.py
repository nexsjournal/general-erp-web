import frappe

from frappe.model.document import Document


class EmailTemplate(Document):
	"""邮件模板：群发/外发主题与正文模板，支持 {{customer_name}} 等变量。"""
