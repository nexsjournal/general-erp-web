# -*- coding: utf-8 -*-
import frappe
from frappe import _


def execute(filters=None):
	"""客户域核心指标 + 按区域分布（公海/热点/跟进/新增）。"""
	from frappe.utils import nowdate
	month_start = nowdate()[:8] + "01"
	overview = [
		("客户总数", frappe.db.count("Customer")),
		("热点客户（星标）", frappe.db.count("Customer", {"is_starred": 1})),
		("公海客户", frappe.db.count("Customer", {"is_public_pool": 1})),
		("私有客户", frappe.db.count("Customer", {"is_public_pool": 0})),
		("本月新增", frappe.db.count("Customer", {"creation": [">=", month_start]})),
		("跟进记录总数", frappe.db.count("Customer Follow Up")),
	]
	last = frappe.db.sql("select max(follow_date) from `tabCustomer Follow Up`", as_list=True)
	overview.append(("最近跟进日期", str(last[0][0]) if last and last[0] else "-"))
	rows = [{"dimension": k, "value": v} for k, v in overview]
	by_territory = frappe.db.sql(
		"select coalesce(territory, '未设置') as territory, count(*) as cnt from `tabCustomer` "
		"group by territory order by cnt desc limit 10", as_dict=True)
	for r in by_territory:
		rows.append({"dimension": "区域 · " + r.territory, "value": r.cnt})
	columns = [
		{"label": _("指标"), "fieldname": "dimension", "fieldtype": "Data"},
		{"label": _("数值"), "fieldname": "value", "fieldtype": "Data"},
	]
	return columns, rows
