# -*- coding: utf-8 -*-
"""工作日历：聚合节假日 / 跟进提醒 / 出运计划 / 商机成交 / 工作检查，按月返回事件。"""
import frappe

from frappe.utils import cstr


@frappe.whitelist()
def get_calendar_events(year, month):
	"""year/month: int；返回 [{date, type, label, doctype, name}]。"""
	year, month = int(year), int(month)
	start = "%d-%02d-01" % (year, month)
	end = ("%d-%02d-01" % (year, month + 1)) if month < 12 else ("%d-01-01" % (year + 1))
	events = []

	# T2-15: 节假日按公司默认 Holiday List 过滤（演示：中国法定节假日-2026）
	company = frappe.db.get_single_value("Global Defaults", "default_company") or frappe.db.get_value("Company", {"disabled": 0}, "name")
	holiday_list = frappe.db.get_value("Company", company, "default_holiday_list") if company else None
	holidays = []
	if holiday_list:
		holidays = frappe.get_all("Holiday", filters={"parent": holiday_list, "holiday_date": ["between", (start, end)]}, fields=["name", "holiday_date", "description"])
	for h in holidays:
		events.append({"date": cstr(h.holiday_date), "type": "holiday", "label": h.description or "节假日", "doctype": "Holiday", "name": h.name})

	fus = frappe.get_all("Customer Follow Up", filters={"next_follow_date": ["between", (start, end)]}, fields=["name", "next_follow_date", "customer", "follow_type"])
	for f in fus:
		cname = frappe.db.get_value("Customer", f.customer, "customer_name") or f.customer
		events.append({"date": cstr(f.next_follow_date), "type": "follow", "label": "跟进 " + cname + "（" + (f.follow_type or "") + "）", "doctype": "Customer Follow Up", "name": f.name})

	if frappe.db.exists("DocType", "Export Shipment"):
		shipments = frappe.get_all("Export Shipment", filters={"etd": ["between", (start, end)]}, fields=["name", "etd", "bl_no"])
		for s in shipments:
			events.append({"date": cstr(s.etd), "type": "shipment", "label": "出运 " + (s.bl_no or s.name) + "（ETD）", "doctype": "Export Shipment", "name": s.name})

	opps = frappe.get_all("Opportunity", filters={"expected_closing": ["between", (start, end)], "status": ["not in", ("Lost", "Converted", "Closed")]}, fields=["name", "expected_closing", "title", "customer_name"])
	for o in opps:
		events.append({"date": cstr(o.expected_closing), "type": "opportunity", "label": "商机成交 " + (o.title or o.customer_name or o.name), "doctype": "Opportunity", "name": o.name})

	checks = frappe.get_all("Work Check", filters={"check_date": ["between", (start, end)]}, fields=["name", "check_date", "title"])
	for c in checks:
		events.append({"date": cstr(c.check_date), "type": "work_check", "label": "工作检查 " + c.title, "doctype": "Work Check", "name": c.name})

	events.sort(key=lambda e: e["date"])
	return events
