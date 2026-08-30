# -*- coding: utf-8 -*-
"""发送跟踪：跟踪像素（打开）+ 点击跳转，写入 Mail / Bulk Email Customer 的打开/点击状态。

- 跟踪像素：/api/method/general_erp.general_erp.mail_tracking.get_pixel?m=<tracking_id>（返回 1x1 GIF）
- 点击跳转：/api/method/general_erp.general_erp.mail_tracking.track_click?m=<tracking_id>&u=<目标地址>（302 跳转）
- tracking_id 规则：单发 = Mail.tracking_id；群发 = BULK:<任务名>:<客户行名>
"""
import base64
import urllib.parse

import frappe
from werkzeug.wrappers import Response
from werkzeug.utils import redirect

# 1x1 透明 GIF
TRANSPARENT_GIF = base64.b64decode("R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")

PIXEL_METHOD = "general_erp.general_erp.mail_tracking.get_pixel"
CLICK_METHOD = "general_erp.general_erp.mail_tracking.track_click"


def make_tracking_id(mail_name):
	return frappe.generate_hash(txt=mail_name, length=16)


def tracked_url(m, target=None):
	"""生成跟踪地址；target 为空返回像素地址，否则返回点击跳转地址。"""
	base = frappe.utils.get_url()
	if not target:
		return f"{base}/api/method/{PIXEL_METHOD}?m={m}"
	return f"{base}/api/method/{CLICK_METHOD}?m={m}&u={urllib.parse.quote(target, safe='')}"


def inject_tracking(base_url, m, html):
	"""向 HTML 正文注入跟踪像素，并把链接改写为点击跳转链接。"""
	if not html:
		return html
	# 点击跳转：href="http..." → href="track?m=..&u=.."
	import re
	def _repl(match):
		return f'href="{tracked_url(m, match.group(1))}"'
	html = re.sub(r'href="(https?://[^"]+)"', _repl, html)
	# 跟踪像素
	pixel = f'<img src="{tracked_url(m)}" width="1" height="1" style="display:none" alt="" />'
	if "</body>" in html:
		html = html.replace("</body>", f"{pixel}</body>")
	else:
		html = html + pixel
	return html


def _mark(target, opened):
	"""target: tracking_id（Mail）或 BULK:<任务>:<行名>；opened=True 记打开，False 记点击。"""
	if not target:
		return
	if str(target).startswith("BULK:"):
		_, task, row = str(target).split(":", 2)
		key = "opened" if opened else "clicked"
		at_key = "opened_at" if opened else "clicked_at"
		try:
			doc = frappe.get_doc("Bulk Email", task)
			for r in doc.customers:
				if r.name == row:
					r.set(key, 1)
					r.set(at_key, frappe.utils.now_datetime())
			doc.save(ignore_permissions=True)
			count_key = "opened_count" if opened else "clicked_count"
			frappe.db.set_value("Bulk Email", task, count_key,
				sum(1 for x in doc.customers if x.get((count_key.replace('_count','')))))
		except Exception:
			frappe.log_error(title=f"群发跟踪失败：{target}")
		return
	m = frappe.db.get_value("Mail", {"tracking_id": target}, ["name", "opened", "clicked"], as_dict=True)
	if not m:
		return
	updates = {}
	if opened and not m.opened:
		updates["opened"] = 1
		updates["opened_at"] = frappe.utils.now_datetime()
	if not opened and not m.clicked:
		updates["clicked"] = 1
		updates["clicked_at"] = frappe.utils.now_datetime()
	if updates:
		frappe.db.set_value("Mail", m.name, updates)


@frappe.whitelist(allow_guest=True)
def get_pixel(m=None):
	"""跟踪像素端点：标记邮件已打开，返回 1x1 透明 GIF。"""
	_mark(m, opened=True)
	return Response(
		TRANSPARENT_GIF,
		mimetype="image/gif",
		headers={"Cache-Control": "no-cache, no-store"},
	)


def _is_safe_redirect_target(url):
	"""防开放重定向：仅允许站内相对路径或白名单域（当前站点域）。"""
	if not url:
		return False
	u = url.strip()
	if u.startswith(("/", "#")) and not u.startswith("//"):
		return True
	try:
		parts = urllib.parse.urlsplit(u)
	except ValueError:
		return False
	if parts.scheme not in ("http", "https") or not parts.hostname:
		return False
	from frappe.utils import get_url
	try:
		local_host = urllib.parse.urlsplit(get_url()).hostname
	except Exception:
		return False
	return parts.hostname == local_host


@frappe.whitelist(allow_guest=True)
def track_click(m=None, u=None):
	"""点击跟踪端点：标记邮件链接已点击，302 跳转目标地址（限站内/本域名）。"""
	_mark(m, opened=False)
	target = urllib.parse.unquote(u or "/")
	if not _is_safe_redirect_target(target):
		target = "/"
	return redirect(target, code=302)
