import frappe
from frappe import _

from frappe.model.document import Document
from frappe.utils import now_datetime

from general_erp.general_erp.mail_tracking import inject_tracking


class BulkEmail(Document):
	"""邮件群发：向客户批量发送邮件，并记录发送统计（营销效果分析）。"""




def _enforce_rate_limits(doc):
	"""频率限制（T06）：按已启用营销账号的日发送上限/单收件人上限校验，0=不限制。"""
	limits = frappe.get_all(
		"Mail Account",
		filters={"enabled": 1},
		fields=["daily_send_limit", "per_recipient_limit"],
	)
	if not limits:
		return
	daily = max((l.daily_send_limit or 0) for l in limits)
	per_recipient = max((l.per_recipient_limit or 0) for l in limits)
	from frappe.utils import nowdate, getdate
	day_start = str(getdate(nowdate()))
	if daily > 0:
		sent_today = frappe.db.sql(
			"select sum(total_count) from `tabBulk Email` "
			"where sent_at >= %s and send_status in ('已发送', '部分失败') and name != %s",
			(day_start, doc.name), as_list=True,
		)[0][0] or 0
		if sent_today + len(doc.customers) > daily:
			frappe.throw(_("超出日发送上限（今日已发 {0}，上限 {1}，本次 {2}）").format(sent_today, daily, len(doc.customers)))
	if per_recipient > 0:
		rows = frappe.db.sql(
			"select c.customer from `tabBulk Email Customer` c "
			"join `tabBulk Email` b on b.name = c.parent "
			"where b.sent_at >= %s and b.send_status in ('已发送', '部分失败') and b.name != %s",
			(day_start, doc.name), as_dict=True,
		)
		counts = {}
		for row in rows:
			counts[row.customer] = counts.get(row.customer, 0) + 1
		for row in doc.customers:
			if counts.get(row.customer, 0) + 1 > per_recipient:
				frappe.throw(_("收件人 {0} 超出单收件人上限（今日已发 {1}，上限 {2}）").format(row.customer, counts.get(row.customer, 0), per_recipient))


@frappe.whitelist()
def send_bulk_email(name):
	"""发送群发任务：逐个收件客户发送（frappe.sendmail 走邮件队列），回写发送统计。"""
	doc = frappe.get_doc("Bulk Email", name)
	if doc.send_status in ("已发送", "部分失败"):
		frappe.throw(_("该群发任务已发送"))
	if not doc.customers:
		frappe.throw(_("请先添加收件客户"))
	_enforce_rate_limits(doc)
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
