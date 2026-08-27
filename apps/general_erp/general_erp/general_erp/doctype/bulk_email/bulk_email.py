import frappe
from frappe import _

from frappe.model.document import Document
from frappe.utils import now_datetime

from general_erp.general_erp.mail_tracking import inject_tracking


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
	tpl = frappe.get_doc("Email Template", doc.template) if doc.template else None
	company = frappe.db.get_single_value("Global Defaults", "company") or ""
	for row in doc.customers:
		email = frappe.db.get_value("Customer", row.customer, "email_id")
		if not email:
			fail += 1
			continue
		customer_name = row.customer_name or row.customer
		subject = (tpl.subject if tpl else doc.subject) or doc.subject
		message = (tpl.body if tpl else (doc.body or "")) or (doc.body or "")
		if tpl:
			subject = subject.replace("{{customer_name}}", customer_name).replace("{{company_name}}", company)
			message = message.replace("{{customer_name}}", customer_name).replace("{{company_name}}", company)
		else:
			subject = subject.replace("{{customer_name}}", customer_name).replace("{{company_name}}", company)
		if doc.track:
			tid = "BULK:%s:%s" % (doc.name, row.name)
			subject = subject  # 主题不注入
			message = inject_tracking(frappe.utils.get_url(), tid, message)
		try:
			frappe.sendmail(recipients=[email], subject=subject, message=message)
			ok += 1
		except Exception:
			fail += 1
	doc.total_count = len(doc.customers)
	doc.success_count = ok
	doc.fail_count = fail
	doc.opened_count = 0
	doc.clicked_count = 0
	doc.send_status = "已发送" if fail == 0 else "部分失败"
	doc.sent_at = now_datetime()
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return {"success": ok, "fail": fail}
