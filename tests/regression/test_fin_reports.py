# -*- coding: utf-8 -*-
"""原生财务报表回归: 三张表(资产负债表/现金流量表/利润表)带当前会计年度过滤器必须直接出数(>0行),
对应前端 T-fin-fy 自动预填能力; 另验证自定义报表目录全部可跑。"""
import sys, os, glob, json, importlib
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa


def current_fy():
	t = str(frappe.utils.nowdate())
	row = frappe.db.sql("SELECT name FROM `tabFiscal Year` WHERE %s BETWEEN year_start_date AND year_end_date ORDER BY year_start_date DESC LIMIT 1", (t,))
	if row:
		return row[0][0]
	row = frappe.db.sql("SELECT name FROM `tabFiscal Year` ORDER BY year_start_date DESC LIMIT 1")
	return row[0][0] if row else None


def main():
	connect()
	r = Results()
	fy = current_fy()
	if not fy:
		r.fail("当前会计年度", "无可用 Fiscal Year")
		return r.summary()
	F = frappe._dict(company=COMPANY, filter_based_on="Fiscal Year", from_fiscal_year=fy,
		to_fiscal_year=fy, periodicity="Yearly", presentation_currency=None, accumulated_values=1)
	for m in ["balance_sheet", "cash_flow", "profit_and_loss_statement"]:
		try:
			mod = importlib.import_module("erpnext.accounts.report." + m + "." + m)
			out = mod.execute(F)
			data = out[1] if isinstance(out, tuple) else out
			assert len(data) > 0, "报表 0 行"
			r.ok("原生财务表-" + m, "%d行 FY=%s" % (len(data), fy))
		except Exception as e:
			r.fail("原生财务表-" + m, e)

	# 自定义报表全跑
	base = os.path.abspath(os.path.join(os.path.dirname(__file__),
		"../../apps/general_erp/general_erp/general_erp/report"))
	ok = fail = 0
	for jf in sorted(glob.glob(base + "/*/*.json")):
		d = json.load(open(jf, encoding="utf-8"))
		if d.get("doctype") != "Report":
			continue
		name = d["name"]
		try:
			mod = importlib.import_module("general_erp.general_erp.report." + name + "." + name)
			mod.execute({})
			ok += 1
		except Exception as e:
			fail += 1
			r.fail("自定义报表-" + name, e)
	if fail == 0:
		r.ok("自定义报表全跑通", "%d个 OK" % ok)
	return r.summary()


if __name__ == "__main__":
	sys.exit(main())
