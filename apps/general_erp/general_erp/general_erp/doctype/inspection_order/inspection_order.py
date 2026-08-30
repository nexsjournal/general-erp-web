import frappe

from frappe import _

from frappe.model.document import Document


class InspectionOrder(Document):
	"""验货单：到货检验；提交时按结论联动（T2-04）。"""

	def validate(self):
		"""conclusion 有值即可提交；不合格且未选处理方案时默认退货。"""
		if self.conclusion == "不合格" and not (self.exception_handling and self.exception_handling != "无"):
			self.exception_handling = "退货"

	def on_submit(self):
		"""不合格 → 生成退货待办给采购；合格 → 可点「生成入库单」。"""
		if self.conclusion == "不合格":
			if not frappe.db.exists("ToDo", {"reference_type": "Inspection Order", "reference_name": self.name}):
				t = frappe.new_doc("ToDo")
				t.update({
					"description": "验货不合格处理：{0}（方案：{1}）\n供应商 {2} 的验货单 {0} 结论为不合格，请按处理方案跟进。".format(
						self.name, self.exception_handling or "退货", self.supplier or ""
					),
					"reference_type": "Inspection Order",
					"reference_name": self.name,
					"priority": "High",
					"status": "Open",
				})
				t.insert(ignore_permissions=True)
				frappe.db.commit()


@frappe.whitelist()
def make_purchase_receipt(inspection_name):
	"""验货合格 → 生成 Purchase Receipt（按采购订单剩余行）。返回新单名。"""
	doc = frappe.get_doc("Inspection Order", inspection_name)
	if doc.docstatus != 1:
		frappe.throw(_("验货单未提交"), frappe.ValidationError)
	if doc.conclusion == "不合格":
		frappe.throw(_("验货不合格，不能生成入库单（处理方案：{0}）").format(doc.exception_handling or "退货"), frappe.ValidationError)
	if not doc.purchase_order:
		frappe.throw(_("未关联采购订单"), frappe.ValidationError)
	if frappe.db.exists("Purchase Receipt", {"purchase_order": doc.purchase_order, "docstatus": ["<", 2]}):
		frappe.throw(_("该采购订单已有未取消的入库单"), frappe.ValidationError)
	po = frappe.get_doc("Purchase Order", doc.purchase_order)
	pr = frappe.new_doc("Purchase Receipt")
	pr.update({
		"company": po.company,
		"supplier": po.supplier,
		"purchase_order": doc.purchase_order,
		"supplier_name": po.supplier_name,
		"schedule_date": frappe.utils.today(),
	})
	for item in po.items:
		pr.append("items", {
			"item_code": item.item_code,
			"qty": item.qty - (item.received_qty or 0),
			"purchase_receipt_item": item.name,
		})
	if not any(i.qty > 0 for i in pr.items):
		frappe.throw(_("采购订单已全部入库"), frappe.ValidationError)
	pr.insert(ignore_permissions=True)
	frappe.db.set_value("Inspection Order", doc.name, "purchase_receipt", pr.name)
	frappe.db.commit()
	return pr.name
