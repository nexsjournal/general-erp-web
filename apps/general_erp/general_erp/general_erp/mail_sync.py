# -*- coding: utf-8 -*-
"""IMAP 收件同步：调度任务定时拉取各邮箱账号的未读邮件，写入 Mail 单据（收件箱/待处理）。"""
import email as email_lib
import email.header
import email.utils
import imaplib

import frappe

from frappe.utils import now_datetime


@frappe.whitelist()
def fetch_incoming_mails():
	"""拉取所有启用邮箱账号的未读邮件；返回 [账号: 新增数量]。"""
	result = {}
	accounts = frappe.get_all("Mail Account", filters={"enabled": 1, "imap_host": ["!=", ""]}, fields=["name", "email_id", "imap_host", "imap_port", "imap_user", "imap_password", "use_ssl", "owner_user"])
	for acct in accounts:
		try:
			n = _fetch_account(acct)
			frappe.db.set_value("Mail Account", acct.name, "last_sync_at", now_datetime())
			result[acct.email_id] = n
		except Exception:
			frappe.log_error(title=f"邮箱同步失败：{acct.email_id}")
			result[acct.email_id] = -1
	frappe.db.commit()
	return result


def _fetch_account(acct):
	created = 0
	port = int(acct.imap_port or 993)
	if acct.use_ssl:
		conn = imaplib.IMAP4_SSL(acct.imap_host, port)
	else:
		conn = imaplib.IMAP4(acct.imap_host, port)
	try:
		conn.login(acct.imap_user or acct.email_id, acct.imap_password)
		conn.select("INBOX")
		typ, data = conn.search(None, "UNSEEN")
		if typ != "OK" or not data or not data[0]:
			return 0
		for num in data[0].split():
			typ, msg_data = conn.fetch(num, "(RFC822)")
			if typ != "OK" or not msg_data:
				continue
			raw = msg_data[0][1]
			msg = email_lib.message_from_bytes(raw)
			message_id = (msg.get("Message-Id") or "").strip()
			if message_id and frappe.db.exists("Mail", {"message_id": message_id}):
				continue
			subject = email.header.decode_header(msg.get("Subject") or "")
			subject = "".join(
				part if isinstance(part, str) else part.decode(enc or "utf-8", "replace")
				for part, enc in subject
			)
			from_addr, _ = email.utils.parseaddr(msg.get("From") or "")
			body = ""
			if msg.is_multipart():
				for part in msg.walk():
					if part.get_content_type() == "text/plain":
						payload = part.get_payload(decode=True)
						if payload:
							body = payload.decode(part.get_content_charset() or "utf-8", "replace")
							break
			else:
				payload = msg.get_payload(decode=True)
				if payload:
					body = payload.decode(msg.get_content_charset() or "utf-8", "replace")
			m = frappe.new_doc("Mail")
			m.update({
				"subject": (subject or "(无主题)")[:140],
				"folder": "收件箱",
				"status": "待处理",
				"sender": acct.owner_user,
				"from_address": from_addr or None,
				"body": body[:20000] or None,
				"message_id": message_id or None,
			})
			m.insert(ignore_permissions=True)
			created += 1
	finally:
		try:
			conn.close()
		except Exception:
			pass
	try:
		conn.logout()
	except Exception:
		pass
	return created
