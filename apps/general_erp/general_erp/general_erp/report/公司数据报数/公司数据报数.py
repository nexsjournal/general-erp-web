# -*- coding: utf-8 -*-
import frappe
from frappe import _


def execute(filters=None):
	from general_erp.general_erp.report_utils import check_report_access
	check_report_access("公司数据报数")
	"""公司数据报数：经营关键指标一览（客户/商机/订单/出运/收付款/库存/费用）。"""
	def one(sql):
		try:
			return frappe.db.sql(sql, as_list=True)[0][0] or 0
		except Exception:
			return 0
	comp = frappe.db.get_single_value('Global Defaults', 'default_company') or '外贸演示公司'
	metrics = [
		("客户总数（含公海）", one("SELECT count(*) FROM `tabCustomer`")),
		("线索总数", one("SELECT count(*) FROM `tabLead`")),
		("在途商机数", one("SELECT count(*) FROM `tabOpportunity` WHERE status NOT IN ('Converted','Lost','Closed')")),
		("销售订单数（已提交）", one("SELECT count(*) FROM `tabSales Order` WHERE docstatus=1")),
		("销售订单金额", one("SELECT coalesce(sum(grand_total),0) FROM `tabSales Order` WHERE docstatus=1")),
		("已交货订单金额", one("SELECT coalesce(sum(grand_total),0) FROM `tabDelivery Note` WHERE docstatus=1")),
		("销售发票金额（已开票）", one("SELECT coalesce(sum(grand_total),0) FROM `tabSales Invoice` WHERE docstatus=1")),
		("已收款金额", one("SELECT coalesce(sum(paid_amount),0) FROM `tabPayment Entry` WHERE payment_type='Receive' AND docstatus=1")),
		("已出运单数", one("SELECT count(*) FROM `tabExport Shipment`")),
		("采购订单金额", one("SELECT coalesce(sum(grand_total),0) FROM `tabPurchase Order` WHERE docstatus=1")),
		("库存商品数", one("SELECT count(DISTINCT item_code) FROM `tabBin` WHERE actual_qty>0")),
		("本月费用报销", one("SELECT coalesce(sum(net_amount),0) FROM `tabExpense Reimbursement` WHERE docstatus=1 AND date >= DATE_FORMAT(NOW(), '%Y-%m-01')")),
	]
	data = [{"metric": m, "value": v, "unit": ""} for m, v in metrics]
	columns = [
		{"label": _("指标"), "fieldname": "metric", "fieldtype": "Data"},
		{"label": _("数值"), "fieldname": "value", "fieldtype": "Float"},
		{"label": _("单位"), "fieldname": "unit", "fieldtype": "Data"},
	]
	return columns, data
