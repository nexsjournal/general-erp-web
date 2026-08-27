import frappe
from frappe import _

from frappe.model.document import Document
from frappe.utils import now_datetime


class BulkEmail(Document):
	"""邮件群发：向客户批量发送邮件，并记录发送统计（营销效果分析）。"""


@frappe.whitelist()
def send_bulk_email(name):
	"""发送群发任务：逐个收件客户发送（frappe.sendmail 走邮件队列），回写发送统计。"""
	doc = frappe.get_doc("Bulk Email", name)
	if doc.send_status in ("已发送", "部分失败"):
		frappe.throw(_("该群发任务已发送"))
	if not doc.customers:
		frappe.throw(_("请先添加收件客户"))
	ok = fail = 0
	for row in doc.customers:
		email = frappe.db.get_value("Customer", row.customer, "email_id")
		if not email:
			fail += 1
			continue
		try:
			frappe.sendmail(recipients=[email], subject=doc.subject, message=doc.body or "")
			ok += 1
		except Exception:
			fail += 1
	doc.total_count = len(doc.customers)
	doc.success_count = ok
	doc.fail_count = fail
	doc.send_status = "已发送" if fail == 0 else "部分失败"
	doc.sent_at = now_datetime()
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return {"success": ok, "fail": fail}
