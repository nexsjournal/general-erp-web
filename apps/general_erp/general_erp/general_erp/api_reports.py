# -*- coding: utf-8 -*-
"""报表辅助 API（只读，登录用户可用）。

T-fin-fy: 三张原生财务报表(资产负债表/利润表/现金流量表)依赖 from_fiscal_year/to_fiscal_year，
首次打开未选会计年度会报"必填"。前端补丁用本接口拿到当前会计年度自动预填。
"""

import frappe


@frappe.whitelist()
def get_current_fiscal_year():
	today = frappe.utils.nowdate()
	row = frappe.db.sql(
		"SELECT name, year_start_date, year_end_date FROM `tabFiscal Year` "
		"WHERE %s BETWEEN year_start_date AND year_end_date ORDER BY year_start_date DESC LIMIT 1",
		(today,),
	)
	if row:
		return {"name": row[0][0], "year_start_date": str(row[0][1]), "year_end_date": str(row[0][2])}
	# 兜底: 取最近开始的会计年度
	row = frappe.db.sql(
		"SELECT name, year_start_date, year_end_date FROM `tabFiscal Year` ORDER BY year_start_date DESC LIMIT 1"
	)
	if row:
		return {"name": row[0][0], "year_start_date": str(row[0][1]), "year_end_date": str(row[0][2])}
	return None
