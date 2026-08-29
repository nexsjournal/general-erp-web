# -*- coding: utf-8 -*-
"""回归测试公共配置。所有测试数据带 TAG 前缀, cleanup.py 统一清理。"""
import frappe
from datetime import date

TAG = "回归测试"
COMPANY = "外贸演示公司"
WH = "Finished Goods - 外"
ITEM = "ITM-004"  # 演示公司普通库存物品
# T-regr-dyn: 动态取当天（2026-08-30 起）。原硬编码日期跨天后采购单 schedule_date
# 变过去日, ERPNext validate_schedule_date 报 "Required By cannot be before Date"。
# 用标准库 date（不依赖 frappe 连接，common.py 在 connect 前即被 import）。
TODAY = date.today().strftime("%Y-%m-%d")


def connect():
	frappe.init(site="general.erp.local", sites_path="sites")
	frappe.connect()
	frappe.set_user("Administrator")


class Results(object):
	def __init__(self):
		self.rows = []

	def ok(self, name, detail=""):
		self.rows.append((name, True, str(detail)))
		print("PASS", name, str(detail)[:90])

	def fail(self, name, err):
		self.rows.append((name, False, str(err)))
		print("FAIL", name, "|", str(err)[:120])

	def summary(self):
		p = sum(1 for r in self.rows if r[1])
		line = "==== %d/%d PASSED ====" % (p, len(self.rows))
		print(line)
		return 0 if p == len(self.rows) else 1
