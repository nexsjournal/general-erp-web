import frappe

from frappe.model.document import Document
from frappe.utils import now_datetime


class Mail(Document):
	"""邮件：工作台内部协作邮件（收件箱/已发送/草稿箱/已删除 + 待处理/待审批）。"""


@frappe.whitelist()
def create_mail(subject, folder, sender, recipient=None, body=None, status="已处理",
		related_doctype=None, related_name=None, track=0, from_address=None):
	"""创建邮件；folder=已发送 且指定收件人时，自动为收件人生成一条待处理收件；track=1 时注入发送跟踪。"""
	from general_erp.general_erp.mail_tracking import inject_tracking, make_tracking_id
	tracking_id = None
	if folder == "已发送" and track:
		tracking_id = make_tracking_id("mail-" + subject + "-" + str(frappe.utils.now_datetime()))
		body = inject_tracking(frappe.utils.get_url(), tracking_id, body)
	# 安全：发件人强制为当前登录用户，防止伪造
	sender = frappe.session.user
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
		"track": 1 if (folder == "已发送" and track) else 0,
		"tracking_id": tracking_id,
		"from_address": from_address or None,
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
def _mail_scope_users():
	"""主管可见发送人集合：本人 + 本部门下属；非主管仅本人。"""
	me = frappe.session.user
	users = {me}
	roles = set(frappe.get_roles())
	if roles & {"Sales Manager", "Purchase Manager", "Stock Manager", "Accounts Manager", "System Manager"}:
		dept = frappe.db.get_value("User", me, "erp_department")
		if dept:
			sub = frappe.get_all("User", filters={"erp_department": dept, "enabled": 1}, fields=["name"])
			users.update(x.name for x in sub)
	return users


@frappe.whitelist()
def get_mails(folder=None, status=None, limit=100):
	"""邮件列表：本人发的 + 发给我的 + （主管）本部门下属发的。"""
	base_filters = []
	if folder:
		base_filters.append(["Mail", "folder", "=", folder])
	if status:
		base_filters.append(["Mail", "status", "=", status])
	me = frappe.session.user
	senders = list(_mail_scope_users())

	def _collect(sender_filter, recipient_filter):
		f = list(base_filters)
		f.append(["Mail", "sender", "in", senders]) if sender_filter else None
		f.append(["Mail", "recipient", "=", me]) if recipient_filter else None
		return frappe.get_all(
			"Mail",
			filters=f,
			fields=["name", "subject", "folder", "status", "sender", "recipient", "sent_at", "creation", "related_doctype", "related_name", "restore_folder", "restore_status", "track", "opened", "clicked", "from_address"],
			order_by="modified desc",
			limit_page_length=int(limit or 100),
		)

	rows = _collect(True, False)
	extra = _collect(False, True)
	seen = set(r.name for r in rows)
	for r in extra:
		if r.name not in seen:
			rows.append(r)
	# 批量查用户姓名（去 N+1，T2-07）
	users = set()
	for r in rows:
		users.add(r.sender)
		if r.recipient:
			users.add(r.recipient)
	name_map = {}
	if users:
		for u in frappe.get_all("User", filters={"name": ["in", list(users)]}, fields=["name", "full_name"]):
			name_map[u.name] = u.full_name or u.name
	for r in rows:
		r["sender_name"] = name_map.get(r.sender, r.sender)
		r["recipient_name"] = name_map.get(r.recipient, r.recipient) if r.recipient else ""
	return rows


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
