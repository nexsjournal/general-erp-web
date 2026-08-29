# -*- coding: utf-8 -*-
"""核心业务链守恒: 销售链(报价→订单→交货→发票→收款 5000元) + 采购链(订单→收货→发票→付款 1500元)。
金额断言防漂移; 单据全提交后库存/GLE 联动。"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa


def main():
	connect()
	r = Results()
	from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry

	# 销售链
	cust = "上海远航贸易有限公司"
	q = frappe.new_doc("Quotation")
	q.update(dict(customer=cust, customer_name=cust, company=COMPANY, title=TAG, sell_to=1,
		currency="CNY", transaction_date=TODAY, naming_series="QT-.FWS.-.#####."))
	q.append("items", dict(item_code=ITEM, qty=10, rate=500))
	q.insert(); frappe.db.commit()

	so = frappe.new_doc("Sales Order")
	so.update(dict(customer=cust, customer_name=cust, company=COMPANY, title=TAG, currency="CNY",
		transaction_date=TODAY, order_type="Sales", naming_series="S-.FWS.-.#####.",
		from_quotation=q.name, delivery_date=TODAY))
	so.append("items", dict(item_code=ITEM, qty=10, rate=500, warehouse=WH, delivery_date=TODAY))
	so.insert(); so.submit(); frappe.db.commit()

	dn = frappe.new_doc("Delivery Note")
	dn.update(dict(customer=cust, customer_name=cust, company=COMPANY, title=TAG, currency="CNY",
		naming_series="DN-.FWS.-.#####."))
	dn.append("items", dict(item_code=ITEM, qty=10, rate=500, warehouse=WH, delivery_date=TODAY))
	dn.insert(); dn.submit(); frappe.db.commit()

	inv = frappe.new_doc("Sales Invoice")
	inv.update(dict(customer=cust, customer_name=cust, company=COMPANY, title=TAG, currency="CNY",
		naming_series="INV-.FWS.-.#####."))
	inv.append("items", dict(item_code=ITEM, qty=10, rate=500, dn=dn.name))
	inv.insert(); inv.submit(); frappe.db.commit()

	pay = get_payment_entry("Sales Invoice", inv.name, party_type="Customer", payment_type="Receive",
		bank_account="Cash - 外", reference_date=TODAY)
	pay.naming_series = "PE-.FWS.-.#####."
	for ref in pay.references:
		ref.allocated_amount = ref.total_amount
	pay.insert(); pay.submit(); frappe.db.commit()
	try:
		assert abs(inv.grand_total - 5000) < 0.01, inv.grand_total
		assert abs(pay.paid_amount - 5000) < 0.01, pay.paid_amount
		r.ok("销售链金额守恒", "发票=%s 收款=%s" % (inv.grand_total, pay.paid_amount))
	except AssertionError as e:
		r.fail("销售链金额守恒", e)

	# 采购链
	sup = "深圳华强电子供应商"
	po = frappe.new_doc("Purchase Order")
	po.update(dict(supplier=sup, supplier_name=sup, company=COMPANY, title=TAG, currency="CNY",
		schedule_date=TODAY, naming_series="PO-.FWS.-.#####.", set_warehouse=WH))
	po.append("items", dict(item_code=ITEM, qty=5, rate=300))
	po.insert(); po.submit(); frappe.db.commit()

	pr = frappe.new_doc("Purchase Receipt")
	pr.update(dict(supplier=sup, supplier_name=sup, company=COMPANY, title=TAG, currency="CNY",
		naming_series="PR-.FWS.-.#####.", set_warehouse=WH))
	pr.append("items", dict(item_code=ITEM, qty=5, rate=300))
	pr.insert(); pr.submit(); frappe.db.commit()

	pi = frappe.new_doc("Purchase Invoice")
	pi.update(dict(supplier=sup, supplier_name=sup, company=COMPANY, title=TAG, currency="CNY",
		naming_series="PINV-.FWS.-.#####.", set_warehouse=WH))
	pi.append("items", dict(item_code=ITEM, qty=5, rate=300, pr=pr.name))
	pi.insert(); pi.submit(); frappe.db.commit()

	pay2 = get_payment_entry("Purchase Invoice", pi.name, party_type="Supplier", payment_type="Pay",
		bank_account="Cash - 外", reference_date=TODAY)
	pay2.naming_series = "PE-.FWS.-.#####."
	for ref in pay2.references:
		ref.allocated_amount = ref.total_amount
	pay2.insert(); pay2.submit(); frappe.db.commit()
	try:
		assert abs(pi.grand_total - 1500) < 0.01, pi.grand_total
		assert abs(pay2.paid_amount - 1500) < 0.01, pay2.paid_amount
		r.ok("采购链金额守恒", "发票=%s 付款=%s" % (pi.grand_total, pay2.paid_amount))
	except AssertionError as e:
		r.fail("采购链金额守恒", e)

	return r.summary()


if __name__ == "__main__":
	sys.exit(main())
