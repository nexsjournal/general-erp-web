import frappe

from frappe.model.document import Document
from frappe.utils import now_datetime


class Mail(Document):
	"""邮件：工作台内部协作邮件（收件箱/已发送/草稿箱/已删除 + 待处理/待审批）。"""


@frappe.whitelist()
def create_mail(subject, folder, sender, recipient=None, body=None, status="已处理",
		related_doctype=None, related_name=None):
	"""创建邮件；folder=已发送 且指定收件人时，自动为收件人生成一条待处理收件。"""
	m = frappe.new_doc("Mail")
	m.update({
		"subject": subject,
		"folder": folder,
		"sender": sender,
		"recipient": recipient or None,
		"body": body or None,
		"status": status,
		"related_doctype": related_doctype or None,
		"related_name": related_name or None,
		"sent_at": now_datetime() if folder == "已发送" else None,
	})
	m.insert(ignore_permissions=True)
	if folder == "已发送" and recipient and recipient != sender:
		inbox = frappe.new_doc("Mail")
		inbox.update({
			"subject": subject,
			"folder": "收件箱",
			"sender": sender,
			"recipient": recipient,
			"body": body or None,
			"status": "待处理",
			"related_doctype": related_doctype or None,
			"related_name": related_name or None,
			"sent_at": m.sent_at,
		})
		inbox.insert(ignore_permissions=True)
	frappe.db.commit()
	return m.name


@frappe.whitelist()
def get_mails(folder=None, status=None, limit=100):
	filters = []
	if folder:
		filters.append(["Mail", "folder", "=", folder])
	if status:
		filters.append(["Mail", "status", "=", status])
	rows = frappe.get_all(
		"Mail",
		filters=filters,
		fields=["name", "subject", "folder", "status", "sender", "recipient", "sent_at", "creation", "related_doctype", "related_name", "restore_folder", "restore_status"],
		order_by="modified desc",
		limit_page_length=int(limit or 100),
	)
	for r in rows:
		r["sender_name"] = frappe.db.get_value("User", r.sender, "full_name") or r.sender
		r["recipient_name"] = frappe.db.get_value("User", r.recipient, "full_name") or r.recipient if r.recipient else ""
	return rows


@frappe.whitelist()
def update_mail(name, folder=None, status=None):
	"""更新邮件文件夹/状态（标记已处理、待审批、删除、恢复等）。"""
	doc = frappe.get_doc("Mail", name)
	if folder:
		if folder == "已删除" and doc.folder != "已删除":
			doc.restore_folder = doc.folder
			doc.restore_status = doc.status
		if folder != "已删除":
			doc.restore_folder = None
			doc.restore_status = None
		doc.folder = folder
	if status:
		doc.status = status
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return doc.as_dict()
