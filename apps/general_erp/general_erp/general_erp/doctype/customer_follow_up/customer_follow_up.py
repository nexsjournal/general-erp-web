import frappe

from frappe.model.document import Document


class CustomerFollowUp(Document):
	"""客户跟进：电话/邮件/微信/拜访等跟进记录，公海回收与移交依据。"""


@frappe.whitelist()
def handover_customer(name, to_user, remark=None):
	"""客户移交：变更负责人并留痕（Comment）。"""
	doc = frappe.get_doc("Customer", name)
	old = doc.get("sales_owner") or doc.owner
	doc.db_set("sales_owner", to_user)
	from frappe.desk.form.utils import add_comment
	add_comment(
		"Customer",
		name,
		"负责人由 {} 移交至 {}{}。".format(old or "（空）", to_user, "；原因：" + remark if remark else ""),
		comment_email=frappe.session.user,
		comment_by=frappe.session.user,
	)
	frappe.db.commit()
	return {"from": old, "to": to_user}


@frappe.whitelist()
def auto_pool_customers(days=None):
	"""公海自动回收：N 天无跟进的私有客户移入公海（调度器每日执行）。"""
	from frappe.utils import nowdate, add_days
	from frappe.desk.form.utils import add_comment
	from general_erp.general_erp.doctype.statistics_settings.statistics_settings import get_pool_days
	if days is None:
		days = get_pool_days()
	rows = frappe.db.sql("""
		SELECT c.name
		FROM `tabCustomer` c
		WHERE c.is_public_pool = 0
		AND c.docstatus = 0
		AND c.modified < %s
	""", (add_days(nowdate(), -int(days)),), as_list=True)
	moved = []
	for (cname,) in rows:
		last = frappe.db.sql("""
			SELECT MAX(follow_date) FROM `tabCustomer Follow Up`
			WHERE customer = %s
		""", (cname,), as_list=True)
		last_follow = last[0][0] if last and last[0] else None
		if last_follow is None or frappe.utils.getdate(last_follow) < frappe.utils.add_days(frappe.utils.nowdate(), -int(days)):
			frappe.db.set_value("Customer", cname, "is_public_pool", 1)
			add_comment(
				"Customer",
				cname,
				"连续 {} 天无跟进，自动移入公海。".format(days),
				comment_email=frappe.session.user,
				comment_by=frappe.session.user,
			)
			moved.append(cname)
	frappe.db.commit()
	return moved
