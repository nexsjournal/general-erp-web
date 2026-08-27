# -*- coding: utf-8 -*-
import frappe
from frappe import _


def execute(filters=None):
	from general_erp.general_erp.report_utils import check_report_access
	check_report_access("客户分析")
	"""客户维度分析：行业/区域/等级分布、公海进出、跟进转化漏斗（P2）。"""
	rows = []

	def add(dimension, value):
		rows.append({"dimension": dimension, "value": value})

	total = frappe.db.count("Customer")
	add("客户总数", total)

	for f in ("industry", "territory", "customer_group"):
		data = frappe.db.sql(
			"select coalesce(%s, '未设置') as k, count(*) as cnt from `tabCustomer` "
			"group by %s order by cnt desc limit 8" % (f, f), as_dict=True)
		for r in data:
			add(f + "分布 · " + r.k, r.cnt)

	add("公海客户", frappe.db.count("Customer", {"is_public_pool": 1}))
	add("私有客户", frappe.db.count("Customer", {"is_public_pool": 0}))
	add("热点客户（星标）", frappe.db.count("Customer", {"is_starred": 1}))

	funnel = [
		("有跟进记录客户", "select count(distinct customer) from `tabCustomer Follow Up` where customer != ''"),
		("本月新增跟进", "select count(*) from `tabCustomer Follow Up` where month(follow_date) = month(curdate()) and year(follow_date) = year(curdate())"),
	]
	for label, sql in funnel:
		res = frappe.db.sql(sql, as_list=True)
		add(label, res[0][0] if res else 0)

	columns = [
		{"label": _("维度"), "fieldname": "dimension", "fieldtype": "Data"},
		{"label": _("数值"), "fieldname": "value", "fieldtype": "Data"},
	]
	return columns, rows
