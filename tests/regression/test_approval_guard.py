# -*- coding: utf-8 -*-
"""T14 审批防绕过守卫回归:
1. PP(生产任务单)审批中, 提交人自己 submit → 拒
2. PP审批中, 审批角色(boss1) submit → 放行到已审批
3. PP审批中, 提交人直接改 workflow_state+docstatus 保存 → 拒(原生validate_workflow或守卫)
4. PO(采购订单)审批中生成收货单 → 拒(未审批订单禁止收货)
5. PO已审批生成收货单 → 放行
所有单据 TAG 前缀, cleanup.py 统一清理。"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa
from frappe.model.workflow import apply_workflow  # noqa

BOM = None


def _bom():
	global BOM
	if not BOM:
		BOM = frappe.db.get_value("BOM", {"item": ITEM, "is_default": 1}, "name")
	return BOM


def make_pp():
	bom = _bom()
	pp = frappe.new_doc("Production Plan")
	pp.update(dict(company=COMPANY, plan_for=ITEM, planned_qty=2, bom_no=bom, title=TAG,
		naming_series="MFG-PP-.FWS.-.#####."))
	pp.append("po_items", dict(item_code=ITEM, bom_no=bom, planned_qty=2,
		stock_uom="Nos", planned_start_date=TODAY))
	pp.insert(); frappe.db.commit()
	return pp.name


def make_po():
	sup = "深圳华强电子供应商"
	po = frappe.new_doc("Purchase Order")
	po.update(dict(supplier=sup, supplier_name=sup, company=COMPANY, title=TAG, currency="CNY",
		schedule_date=TODAY, naming_series="PO-.FWS.-.#####.", set_warehouse=WH))
	po.append("items", dict(item_code=ITEM, qty=2, rate=300))
	po.insert(); frappe.db.commit()
	return po.name


def main():
	connect()
	r = Results()

	# 1. PP审批中 + 提交人 stock1 自己 submit → 拒
	frappe.set_user("Administrator")
	name = make_pp()
	frappe.set_user("stock1@demo.com")
	apply_workflow(frappe.get_doc("Production Plan", name), "提交审批")
	frappe.db.commit()
	assert frappe.db.get_value("Production Plan", name, "workflow_state") == "审批中"
	try:
		frappe.get_doc("Production Plan", name).submit()
		frappe.db.rollback()
		r.fail("PP审批中-submit人自己submit被拒", "未被拦截")
	except frappe.exceptions.ValidationError as e:
		frappe.db.rollback()
		r.ok("PP审批中-submit人自己submit被拒", str(e)[:60])

	# 2. PP审批中 + boss1(审批角色) submit → 放行
	frappe.set_user("Administrator")
	name2 = make_pp()
	frappe.set_user("stock1@demo.com")
	apply_workflow(frappe.get_doc("Production Plan", name2), "提交审批")
	frappe.db.commit()
	frappe.set_user("boss1@demo.com")
	try:
		frappe.get_doc("Production Plan", name2).submit()
		frappe.db.commit()
		state = frappe.db.get_value("Production Plan", name2, "workflow_state")
		if state == "已审批":
			r.ok("PP审批中-审批人submit放行", "state=已审批")
		else:
			r.fail("PP审批中-审批人submit放行", "state=%s" % state)
	except Exception as e:
		frappe.db.rollback()
		r.fail("PP审批中-审批人submit放行", e)

	# 3. PP审批中 + 提交人直接改状态保存 → 拒
	frappe.set_user("Administrator")
	name3 = make_pp()
	frappe.set_user("stock1@demo.com")
	apply_workflow(frappe.get_doc("Production Plan", name3), "提交审批")
	frappe.db.commit()
	try:
		doc = frappe.get_doc("Production Plan", name3)
		doc.docstatus = 1
		doc.workflow_state = "已审批"
		doc.save(ignore_permissions=True)
		frappe.db.rollback()
		r.fail("PP审批中-直接改状态保存被拒", "未被拦截")
	except frappe.exceptions.ValidationError as e:
		frappe.db.rollback()
		r.ok("PP审批中-直接改状态保存被拒", str(e)[:60])

	# 4. PO审批中生成收货单 → 拒
	frappe.set_user("Administrator")
	po_name = make_po()
	frappe.set_user("purchase1@demo.com")
	apply_workflow(frappe.get_doc("Purchase Order", po_name), "提交审批")
	frappe.db.commit()
	assert frappe.db.get_value("Purchase Order", po_name, "workflow_state") == "审批中"
	try:
		from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_receipt
		pr = make_purchase_receipt(po_name)
		pr.insert()
		frappe.db.rollback()
		r.fail("PO审批中-生成收货单被拒", "未被拦截")
	except frappe.exceptions.ValidationError as e:
		frappe.db.rollback()
		msg = str(e)
		if "未审批订单禁止收货" in msg or "不能生成收货单过账" in msg:
			r.ok("PO审批中-生成收货单被拒", msg[:60])
		else:
			r.fail("PO审批中-生成收货单被拒", "拦截了但不是守卫: " + msg[:60])

	# 5. PO已审批生成收货单 → 放行
	frappe.set_user("Administrator")
	po_name2 = make_po()
	frappe.set_user("purchase1@demo.com")
	apply_workflow(frappe.get_doc("Purchase Order", po_name2), "提交审批")
	frappe.db.commit()
	frappe.set_user("boss1@demo.com")
	apply_workflow(frappe.get_doc("Purchase Order", po_name2), "审批")
	frappe.db.commit()
	assert frappe.db.get_value("Purchase Order", po_name2, "workflow_state") == "已审批"
	frappe.set_user("purchase1@demo.com")
	try:
		from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_receipt
		pr = make_purchase_receipt(po_name2)
		pr.insert()
		pr.submit()
		frappe.db.commit()
		r.ok("PO已审批-生成收货单放行", pr.name)
	except Exception as e:
		frappe.db.rollback()
		r.fail("PO已审批-生成收货单放行", e)

	return r.summary()


if __name__ == "__main__":
	sys.exit(main())
