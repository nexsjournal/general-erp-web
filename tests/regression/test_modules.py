# -*- coding: utf-8 -*-
"""全模块 CRUD 回归(防"只测销售采购"盲区): 产品/客户+跟进/财务报销/生产工单/邮件/组织员工/
外贸出运+单证+基础数据/线索/商机/群发/OA/公告。产品自由度: 无海关/序列/批次字段卡传统产品。"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa


def main():
	connect()
	r = Results()

	def step(name, fn):
		try:
			r.ok(name, fn())
		except Exception as e:
			r.fail(name, e)

	# 产品(传统产品: 无海关编码/序列/批次也能建)
	def _item():
		i = frappe.new_doc("Item")
		i.update(dict(item_code=TAG + "-ITM", item_name=TAG + "商品", stock_uom="Unit",
			is_stock_item=0, item_group="Products"))
		i.insert(); frappe.db.commit()
		return i.name
	step("产品-创建商品(无海关/批次字段)", _item)

	def _cust():
		c = frappe.new_doc("Customer")
		c.update(dict(customer_name=TAG + "客户", customer_type="Company", territory="China"))
		c.insert(); frappe.db.commit()
		fu = frappe.new_doc("Customer Follow Up")
		fu.update(dict(customer=c.name, subject=TAG + "跟进", content=TAG, notes=TAG, follow_up_date=TODAY))
		fu.insert(); frappe.db.commit()
		return c.name
	step("客户-创建+跟进", _cust)

	def _lead():
		l = frappe.new_doc("Lead")
		l.lead_name = TAG + "线索"; l.territory = "China"; l.status = "Open"
		l.insert(); frappe.db.commit()
		return l.name
	step("线索-创建", _lead)

	def _opp():
		cust = frappe.db.get_value("Customer", {"customer_type": "Company"}, "name")
		n = frappe.db.get_value("Customer", cust, "customer_name")
		o = frappe.new_doc("Opportunity")
		o.party_type = "Customer"; o.party = cust; o.party_name = n
		o.company = COMPANY; o.opportunity_from = "Customer"; o.status = "Open"; o.transaction_date = TODAY
		i = o.append("items", {}); i.item_code = ITEM; i.rate = 100; i.qty = 1
		o.insert(); frappe.db.commit()
		return o.name
	step("商机-创建", _opp)

	def _exp():
		exp = frappe.new_doc("Expense Reimbursement")
		exp.company = COMPANY; exp.expense_date = TODAY; exp.applicant = "Administrator"
		exp.expense_type = "其他"; exp.amount = 100; exp.description = TAG + "报销"
		exp.insert(); frappe.db.commit()
		assert abs(exp.amount - 100) < 0.01, exp.amount
		return exp.name
	step("财务-费用报销(金额100元)", _exp)

	def _wo():
		bom = frappe.db.get_value("BOM", {"company": COMPANY}, "name")
		if not bom:
			raw = frappe.new_doc("Item")
			raw.update(dict(item_code=TAG + "-RAW", item_name=TAG + "原料", stock_uom="Unit",
				is_stock_item=1, item_group="Raw Material")); raw.insert()
			prod = frappe.new_doc("Item")
			prod.update(dict(item_code=TAG + "-PRD", item_name=TAG + "成品", stock_uom="Unit",
				is_stock_item=1, item_group="Products")); prod.insert(); frappe.db.commit()
			bd = frappe.new_doc("BOM")
			bd.item = prod.item_code; bd.item_name = prod.item_name; bd.company = COMPANY; bd.quantity = 1; bd.is_default = 1
			bi = bd.append("items", {}); bi.item_code = raw.item_code; bi.qty = 2
			bd.insert(); frappe.db.commit(); bom = bd.name
		wo = frappe.new_doc("Work Order")
		wo.bom_no = bom; wo.company = COMPANY; wo.production_item = ITEM; wo.planned_start_date = TODAY
		wo.fg_warehouse = WH; wo.source_warehouse = WH; wo.planned_qty = 5
		wo.insert(); frappe.db.commit()
		return wo.name
	step("生产-工单(BOM)", _wo)

	def _mail():
		m = frappe.new_doc("Mail")
		m.update(dict(subject=TAG + "邮件", folder="收件箱", sender="Administrator",
			recipient="Administrator", body=TAG))
		m.insert(); frappe.db.commit()
		return m.name
	step("邮件-创建", _mail)

	def _emp():
		e = frappe.new_doc("Employee")
		e.first_name = TAG; e.employee_name = TAG + "员"; e.company = COMPANY
		e.gender = "Male"; e.date_of_birth = "1990-01-01"; e.date_of_joining = "2026-01-01"
		e.insert(); frappe.db.commit()
		return e.name
	step("组织-创建员工", _emp)

	def _ship():
		cust = frappe.db.get_value("Customer", {"customer_type": "Company"}, ["name", "customer_name"], as_dict=True)
		s = frappe.new_doc("Export Shipment")
		s.title = TAG; s.company = COMPANY; s.customer = cust["name"]; s.customer_name = cust["customer_name"]
		s.shipment_date = TODAY
		si = s.append("items", {}); si.item_code = ITEM; si.qty = 10; si.rate = 500
		s.insert(); frappe.db.commit()
		return s.name
	step("外贸-出运明细", _ship)

	def _td():
		d = frappe.new_doc("Trade Document")
		d.title = TAG; d.company = COMPANY; d.document_type = "Commercial Invoice"; d.shipment_date = TODAY
		d.insert(); frappe.db.commit()
		return d.name
	step("外贸-单证制作", _td)

	def _tdf():
		made = []
		for dt, fields in [("HS Code", dict(hs_code="6109100010", product_name=TAG + "针织衫")),
				("Incoterms", dict(code=TAG[:4] + "1", chinese_name=TAG + "贸易术语")),
				("Service Provider", dict(provider_name=TAG + "服务商", provider_type="货代"))]:
			try:
				d = frappe.new_doc(dt); d.update(fields); d.insert(); frappe.db.commit(); made.append(dt)
			except Exception as e:
				r.fail("外贸基础数据-" + dt, e)
			return ",".join(made)
	step("外贸基础数据(海关编码/贸易术语/服务商)", _tdf)

	def _be():
		cust = frappe.db.get_value("Customer", {"customer_type": "Company"}, "name")
		b = frappe.new_doc("Bulk Email")
		b.subject = TAG + "群发"; b.message = "<p>%s</p>" % TAG
		b.append("customers", {}).customer = cust
		b.insert(); frappe.db.commit()
		return b.name
	step("营销-群发模板", _be)

	def _wc():
		wc = frappe.new_doc("Work Check")
		wc.title = TAG + "检查"; wc.check_date = TODAY; wc.assignee = "Administrator"
		wc.append("items", {}).item_name = "考勤"
		wc.insert(); frappe.db.commit()
		return wc.name
	step("OA-工作检查", _wc)

	def _ann():
		a = frappe.new_doc("Announcement")
		a.title = TAG + "公告"; a.content = "<p>测试</p>"
		a.insert(); frappe.db.commit()
		return a.name
	step("公告-创建", _ann)

	# 工作台数字卡可加载
	def _cards():
		cards = frappe.get_all("Number Card", fields=["name"])
		return "%d张" % len(cards)
	step("工作台-数字卡", _cards)

	return r.summary()


if __name__ == "__main__":
	sys.exit(main())
