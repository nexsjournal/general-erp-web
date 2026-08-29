# -*- coding: utf-8 -*-
"""回归测试公共配置。所有测试数据带 TAG 前缀, cleanup.py 统一清理。"""
import frappe

TAG = "回归测试"
COMPANY = "外贸演示公司"
WH = "Finished Goods - 外"
ITEM = "ITM-004"  # 演示公司普通库存物品
TODAY = "2026-08-29"


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
