# -*- coding: utf-8 -*-
import frappe
from frappe import _


def execute(filters=None):
	from general_erp.general_erp.report_utils import check_report_access
	check_report_access("感兴趣分析")
	"""客户对产品的兴趣度：询盘数、报价次数（兴趣信号）、兴趣排行（P2）。"""
	rows = []

	def add(item, inquiries, quotes):
		rows.append({"item": item, "inquiries": inquiries, "quotes": quotes, "total": (inquiries or 0) + (quotes or 0)})

	inq = frappe.db.sql(
		"select item_code, count(*) as c from `tabRequest for Quotation Item` where item_code != '' "
		"group by item_code order by c desc limit 15", as_dict=True)
	qu = frappe.db.sql(
		"select item_code, count(*) as c from `tabQuotation Item` where item_code != '' and docstatus < 2 "
		"group by item_code order by c desc limit 15", as_dict=True)
	items = sorted({r.item_code for r in inq} | {r.item_code for r in qu},
				 key=lambda i: -((next((r.c for r in inq if r.item_code == i), 0)) + (next((r.c for r in qu if r.item_code == i), 0))))
	for i in items[:15]:
		add(i,
			next((r.c for r in inq if r.item_code == i), 0),
			next((r.c for r in qu if r.item_code == i), 0))
	if not items:
		add("（暂无询盘/报价兴趣数据）", 0, 0)

	columns = [
		{"label": _("产品"), "fieldname": "item", "fieldtype": "Data"},
		{"label": _("询盘数"), "fieldname": "inquiries", "fieldtype": "Int"},
		{"label": _("报价次数"), "fieldname": "quotes", "fieldtype": "Int"},
		{"label": _("兴趣信号合计"), "fieldname": "total", "fieldtype": "Int"},
	]
	return columns, rows
