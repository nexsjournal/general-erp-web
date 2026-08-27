# -*- coding: utf-8 -*-
import frappe
from frappe import _


def execute(filters=None):
	from general_erp.general_erp.report_utils import check_report_access
	check_report_access("员工业绩排行")
	"""按客户负责人排名：客户数、跟进数、订单数、订单额（已提交销售订单）。"""
	rows = frappe.db.sql(
		"""SELECT coalesce(c.sales_owner, '（未分配）') AS owner,
			count(distinct c.name) AS customer_count,
			(SELECT count(*) FROM `tabCustomer Follow Up` f WHERE f.customer = c.name) AS follow_count,
			coalesce((SELECT count(*) FROM `tabSales Order` s
				WHERE s.customer = c.name AND s.docstatus = 1), 0) AS order_count,
			coalesce((SELECT sum(s.grand_total) FROM `tabSales Order` s
				WHERE s.customer = c.name AND s.docstatus = 1), 0) AS order_amount
		FROM `tabCustomer` c
		WHERE c.docstatus = 0
		GROUP BY owner
		ORDER BY order_amount DESC""", as_dict=True)
	data = []
	for r in rows:
		data.append({
			"owner": r.owner, "customer_count": r.customer_count,
			"follow_count": r.follow_count, "order_count": r.order_count,
			"order_amount": r.order_amount,
		})
	columns = [
		{"label": _("负责人"), "fieldname": "owner", "fieldtype": "Data"},
		{"label": _("客户数"), "fieldname": "customer_count", "fieldtype": "Int"},
		{"label": _("跟进数"), "fieldname": "follow_count", "fieldtype": "Int"},
		{"label": _("订单数"), "fieldname": "order_count", "fieldtype": "Int"},
		{"label": _("订单额"), "fieldname": "order_amount", "fieldtype": "Currency"},
	]
	return columns, data
