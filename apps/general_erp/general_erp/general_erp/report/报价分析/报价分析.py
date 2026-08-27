# -*- coding: utf-8 -*-
import frappe
from frappe import _


def execute(filters=None):
	from general_erp.general_erp.report_utils import check_report_access
	check_report_access("报价分析")
	"""产品被报价使用情况：报价次数、报价金额、报价→订单转化（P2）。"""
	month_start = frappe.utils.nowdate()[:8] + "01"
	rows = []

	q = frappe.db.sql(
		"select item_code, count(*) as cnt, sum(qi.amount) as approx_amount "
		"from `tabQuotation Item` qi join `tabQuotation` q on q.name = qi.parent "
		"where qi.item_code != '' and q.docstatus < 2 group by qi.item_code order by cnt desc limit 15", as_dict=True)
	s = frappe.db.sql(
		"select item_code, count(*) as cnt from `tabSales Order Item` where item_code != '' and docstatus < 2 "
		"group by item_code", as_dict=True)
	so_map = {r.item_code: r.cnt for r in s}

	total_q = frappe.db.sql("select count(*) from `tabQuotation` where docstatus < 2", as_list=True)[0][0]
	month_q = frappe.db.sql("select count(*) from `tabQuotation` where docstatus < 2 and date(transaction_date) >= %s", (month_start,), as_list=True)[0][0]
	month_so = frappe.db.sql("select count(*) from `tabSales Order` where docstatus < 2 and date(transaction_date) >= %s", (month_start,), as_list=True)[0][0]
	total_so = frappe.db.sql("select count(*) from `tabSales Order` where docstatus < 2", as_list=True)[0][0]

	for r in q:
		ord_cnt = so_map.get(r.item_code, 0)
		conv = round(ord_cnt * 100.0 / r.cnt, 1) if r.cnt else 0
		rows.append({
			"item": r.item_code, "cnt": r.cnt,
			"amount": int(r.approx_amount or 0), "orders": ord_cnt, "conversion": conv,
		})
	rows.append({"item": _("合计·报价单（有效）"), "cnt": total_q, "amount": 0, "orders": 0, "conversion": 0})
	rows.append({"item": _("本月报价单 / 本月订单"), "cnt": month_q, "amount": 0, "orders": month_so, "conversion": 0})
	conv_all = round(total_so * 100.0 / total_q, 1) if total_q else 0
	rows.append({"item": _("整体报价→订单转化率 %"), "cnt": 0, "amount": 0, "orders": 0, "conversion": conv_all})

	columns = [
		{"label": _("产品 / 汇总"), "fieldname": "item", "fieldtype": "Data"},
		{"label": _("报价次数"), "fieldname": "cnt", "fieldtype": "Int"},
		{"label": _("报价金额(近似)"), "fieldname": "amount", "fieldtype": "Int"},
		{"label": _("订单次数"), "fieldname": "orders", "fieldtype": "Int"},
		{"label": _("转化率%"), "fieldname": "conversion", "fieldtype": "Float"},
	]
	return columns, rows
