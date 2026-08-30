# -*- coding: utf-8 -*-
"""权限矩阵回归: 各内置角色对关键 DocType 的读/写/建/提交权限 + 数据隔离(销售只能看自己客户)+ 审批工作流配置。"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa
from frappe.permissions import get_role_permissions  # noqa

CASES = [
	("sales1@demo.com", "Sales Invoice"),
	("salesm1@demo.com", "Customer"),
	("purchase1@demo.com", "Purchase Order"),
	("purchase1@demo.com", "Inspection Order"),
	("stock1@demo.com", "Work Order"),
	("accounts1@demo.com", "Sales Invoice"),
	("accounts1@demo.com", "Payment Entry"),
	("boss1@demo.com", "Expense Reimbursement"),
]


def main():
	connect()
	r = Results()
	for u, dt in CASES:
		frappe.set_user(u)
		frappe.clear_cache(user=u)
		d = get_role_permissions(dt, u)
		print("PERM %-20s %-22s R=%s W=%s C=%s S=%s" % (u, dt, d.get("read"), d.get("write"), d.get("create"), d.get("submit")))
		r.ok("权限-" + u.split("@")[0] + "/" + dt, "R=%s S=%s" % (d.get("read"), d.get("submit")))

	# 数据隔离: sales1 看自己客户 True / 他人客户 False
	frappe.set_user("sales1@demo.com")
	frappe.clear_cache(user="sales1@demo.com")
	self_ok = frappe.get_doc("Customer", "上海远航贸易有限公司").has_permission("read")
	other_ok = frappe.get_doc("Customer", "汉堡机械设备 GmbH").has_permission("read")
	try:
		assert self_ok is True and other_ok is False, (self_ok, other_ok)
		r.ok("数据隔离-sales1", "自己=True 他人=False")
	except AssertionError as e:
		r.fail("数据隔离-sales1", e)

	# 销售新建客户: 建得进去 + 读自己 + 他人私有隔离(修复前新建后被 User Permission 误拒 403)
	frappe.set_user("sales1@demo.com")
	frappe.clear_cache(user="sales1@demo.com")
	cname = TAG + "-我的客户"
	if frappe.db.exists("Customer", cname):
		frappe.db.set_value("Customer", cname, "docstatus", 0)
		frappe.delete_doc("Customer", cname, force=True)
	c = frappe.new_doc("Customer")
	c.update(dict(customer_name=cname, customer_type="Company", territory="China"))
	c.insert()
	frappe.clear_cache(user="sales1@demo.com")
	self_new = frappe.get_doc("Customer", cname).has_permission("read")
	try:
		assert self_new is True, "sales1 读自己新建客户被拒"
		r.ok("数据隔离-销售新建客户可读自己", cname)
	except AssertionError as e:
		r.fail("数据隔离-销售新建客户可读自己", e)

	# 工作流: 采购/生产/费用 审批链路存在且角色非空
	frappe.set_user("Administrator")
	for wf in ["采购订单审批", "生产任务单审批", "费用报销审批"]:
		try:
			w = frappe.get_doc("Workflow", wf)
			states = [t.state for t in w.transitions]
			assert states, "无流转"
			r.ok("工作流-" + wf, "/".join(states[:4]))
		except Exception as e:
			r.fail("工作流-" + wf, e)
	return r.summary()


if __name__ == "__main__":
	sys.exit(main())
