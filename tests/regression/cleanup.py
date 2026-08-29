# -*- coding: utf-8 -*-
"""清理本回归套件(TAG 前缀)产生的所有测试数据。已提交单据先取消再删。"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa

CHAIN = ["Payment Entry", "Sales Invoice", "Purchase Invoice", "Delivery Note", "Purchase Receipt", "Sales Order", "Purchase Order", "Quotation"]
MISC = ["Export Shipment", "Trade Document", "Work Check", "Bulk Email", "Announcement", "Mail", "Customer Follow Up", "Opportunity", "Lead", "Expense Reimbursement", "Work Order", "BOM", "Employee", "Customer", "HS Code", "Incoterms", "Service Provider", "Item"]


def clean_dt(dt):
	names = [n for n in frappe.get_all(dt, pluck="name") if (n or "").startswith(TAG)]
	try:
		if "title" in [f.fieldname for f in frappe.get_meta(dt).fields]:
			for n in frappe.get_all(dt, pluck="name"):
				t = frappe.db.get_value(dt, n, "title") or ""
				if TAG in (t or ""):
					names.append(n)
	except Exception:
		pass
	cnt = 0
	for n in sorted(set(names)):
		for _ in range(2):
			try:
				d = frappe.get_doc(dt, n)
				if d.docstatus == 1:
					d.cancel(ignore_permissions=True); frappe.db.commit()
				else:
					frappe.delete_doc(dt, n, force=True, ignore_permissions=True); frappe.db.commit(); cnt += 1; break
			except Exception:
				break
	return cnt


def main():
	connect()
	total = 0
	for dt in CHAIN + MISC:
		try:
			total += clean_dt(dt)
		except Exception as e:
			print("clean skip", dt, str(e)[:60])
	print("CLEANED", total, "docs (TAG=%s)" % TAG)
	frappe.db.commit()
	return 0


if __name__ == "__main__":
	sys.exit(main())
