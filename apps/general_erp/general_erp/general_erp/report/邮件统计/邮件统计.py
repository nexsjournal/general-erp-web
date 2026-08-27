# -*- coding: utf-8 -*-
import frappe
from frappe import _


def execute(filters=None):
	"""邮件中心运营指标：按文件夹/状态分布 + 本月发送量。"""
	from frappe.utils import nowdate
	month_start = nowdate()[:8] + "01"
	rows = []
	for folder in ["收件箱", "已发送", "草稿箱", "已删除"]:
		cnt = frappe.db.count("Mail", {"folder": folder})
		rows.append({"dimension": "文件夹 · " + folder, "value": cnt})
	for st in ["待处理", "待审批", "已处理"]:
		cnt = frappe.db.count("Mail", {"status": st})
		rows.append({"dimension": "状态 · " + st, "value": cnt})
	sent_month = frappe.db.count("Mail", {"folder": "已发送", "sent_at": [">=", month_start]})
	rows.append({"dimension": "本月发送", "value": sent_month})
	bulk = frappe.db.count("Bulk Email")
	ok = frappe.db.sql("select coalesce(sum(success_count),0), coalesce(sum(total_count),0) from `tabBulk Email`", as_list=True)
	rows.append({"dimension": "群发任务数", "value": bulk})
	if ok and ok[0]:
		rows.append({"dimension": "群发成功率", "value": (str(round(ok[0][0] * 100.0 / ok[0][1], 1)) + "%") if ok[0][1] else "-"})
	columns = [
		{"label": _("指标"), "fieldname": "dimension", "fieldtype": "Data"},
		{"label": _("数值"), "fieldname": "value", "fieldtype": "Data"},
	]
	return columns, rows
