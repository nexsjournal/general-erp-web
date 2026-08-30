# -*- coding: utf-8 -*-
import frappe
from frappe import _


def execute(filters=None):
	from general_erp.general_erp.report_utils import check_report_access
	check_report_access("群发效果")
	"""邮件群发效果分析：发送成功率、打开率、点击率。"""
	rows = frappe.db.sql(
		"SELECT be.name, be.subject, be.sent_at, be.send_status, be.total_count, "
		"be.success_count, be.fail_count, be.opened_count, be.clicked_count "
		"FROM `tabBulk Email` be ORDER BY be.sent_at DESC", as_dict=True)
	data = []
	for r in rows:
		total = r.total_count or 0
		data.append({
			"name": r.name, "subject": r.subject or "", "sent_at": str(r.sent_at or "")[:16],
			"send_status": r.send_status or "",
			"total": total, "success": r.success_count or 0, "fail": r.fail_count or 0,
			"success_rate": str(round((r.success_count or 0) * 100.0 / total, 1)) + "%" if total else "-",
			"opened": r.opened_count or 0, "clicked": r.clicked_count or 0,
			"open_rate": str(round((r.opened_count or 0) * 100.0 / total, 1)) + "%" if total else "-",
			"click_rate": str(round((r.clicked_count or 0) * 100.0 / total, 1)) + "%" if total else "-",
		})
	columns = [
		{"label": _("群发任务"), "fieldname": "name", "fieldtype": "Link", "options": "Bulk Email"},
		{"label": _("主题"), "fieldname": "subject", "fieldtype": "Data"},
		{"label": _("发送时间"), "fieldname": "sent_at", "fieldtype": "Data"},
		{"label": _("状态"), "fieldname": "send_status", "fieldtype": "Data"},
		{"label": _("收件数"), "fieldname": "total", "fieldtype": "Int"},
		{"label": _("成功"), "fieldname": "success", "fieldtype": "Int"},
		{"label": _("失败"), "fieldname": "fail", "fieldtype": "Int"},
		{"label": _("成功率"), "fieldname": "success_rate", "fieldtype": "Data"},
		{"label": _("已打开"), "fieldname": "opened", "fieldtype": "Int"},
		{"label": _("已点击"), "fieldname": "clicked", "fieldtype": "Int"},
		{"label": _("打开率"), "fieldname": "open_rate", "fieldtype": "Data"},
		{"label": _("点击率"), "fieldname": "click_rate", "fieldtype": "Data"},
	]
	return columns, data
