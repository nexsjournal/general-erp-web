from frappe import _
import frappe
from frappe.model.document import Document

# 出运状态机：只允许沿 草稿→已订舱→已出运→已清关→已交付 前进
STATUS_ORDER = ["草稿", "已订舱", "已出运", "已清关", "已交付"]


class ExportShipment(Document):
	def before_validate(self):
		self._validate_status_flow()

	def _validate_status_flow(self):
		if not self.status:
			self.status = "草稿"
		if self.status not in STATUS_ORDER:
			frappe.throw(_("无效状态：{0}").format(self.status), title=_("出运状态"))
		if self.is_new():
			return
		# 旧状态以 DB 为准（save 验证时新值尚未落库；db_set/set_value 不经过本校验）
		prev = frappe.db.get_value("Export Shipment", self.name, "status")
		if prev not in STATUS_ORDER:
			prev = "草稿"
		cur_i, prev_i = STATUS_ORDER.index(self.status), STATUS_ORDER.index(prev)
		if cur_i < prev_i:
			frappe.throw(
				_("出运状态只允许前进：不能从 {0} 改回 {1}").format(prev, self.status),
				title=_("出运状态"),
			)
		if cur_i > prev_i + 1:
			frappe.throw(
				_("出运状态只允许逐级前进：不能从 {0} 直接改到 {1}").format(prev, self.status),
				title=_("出运状态"),
			)


@frappe.whitelist()
def make_shipment_from_sales_order(sales_order_name):
	"""从销售订单生成出运单：复制客户、SO 关联与明细行。返回新建 Shipment 名称。"""
	so = frappe.get_doc("Sales Order", sales_order_name)
	if not so.items:
		frappe.throw(_("销售订单无明细，无法生成出运单"), frappe.ValidationError)
	for row in so.items:
		if row.delivered_qty >= (row.qty or 0) and row.qty:
			frappe.throw(_("{0} 已全部出运，不能重复生成").format(row.item_code), frappe.ValidationError)
	s = frappe.new_doc("Export Shipment")
	s.update({
		"customer": so.customer,
		"sales_order": so.name,
	})
	for row in so.items:
		s.append("items", {
			"item_code": row.item_code,
			"item_name": row.item_name,
			"qty": row.qty,
			"uom": row.uom,
		})
	s.insert()
	frappe.msgprint(_("已生成出运单 {0}").format(s.name), indicator="success", alert=True)
	return s.name
