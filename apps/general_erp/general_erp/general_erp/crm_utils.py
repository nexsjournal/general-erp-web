# -*- coding: utf-8 -*-
"""客户工具：合并 / 共享 / 移交留痕。"""
import frappe

from frappe import _
from frappe.utils import now_datetime


def _require_manager():
	if frappe.session.user == "Administrator" or "System Manager" in frappe.get_roles():
		return
	frappe.throw(_("仅系统管理员或客户负责人可执行此操作"), frappe.PermissionError)


@frappe.whitelist()
def merge_customers(keep, drop):
	"""合并重复客户：drop（逗号分隔）并入 keep；跟进/商机/报价/订单/邮件改挂主记录，源记录停用并标记。整体事务，失败回滚。"""
	_require_manager()
	keep = frappe.db.get_value("Customer", keep, "name")
	drops = [d.strip() for d in str(drop).split(",") if d.strip()]
	if not keep or not drops:
		frappe.throw(_("请指定主客户与待合并客户"))
	if keep in drops:
		frappe.throw(_("主客户不能出现在待合并列表中"))
	frappe.db.rollback()
	try:
		keep_doc = frappe.get_doc("Customer", keep)
		for d in drops:
			doc = frappe.get_doc("Customer", d)
			if doc.get("merged_into"):
				frappe.throw(_("{0} 已合并到 {1}，不能重复合并").format(d, doc.merged_into))
			# 业务单据改挂主客户（字段名以各 DocType 实际为准）
			for dt, field in [
				("Customer Follow Up", "customer"),
				("Opportunity", "party_name"),
				("Quotation", "party_name"),
				("Sales Order", "customer"),
				("Delivery Note", "customer"),
				("Sales Invoice", "customer"),
				("Export Shipment", "customer"),
			]:
				meta = frappe.get_meta(dt)
				if meta.get_field(field):
					frappe.db.set_value(dt, {field: d, "docstatus": ["<", 2]}, field, keep, update_modified=False)
			# 付款单：party_type=Customer 的 party 改挂
			frappe.db.set_value("Payment Entry",
				{"party_type": "Customer", "party": d, "docstatus": ["<", 2]},
				"party", keep, update_modified=False)
			frappe.db.set_value("Mail", {"related_name": d, "related_doctype": "Customer"}, "related_name", keep, update_modified=False)
			frappe.db.set_value("Lead", {"customer": d}, "customer", keep, update_modified=False)
			# 源记录停用 + 标记
			doc.merged_into = keep
			doc.disabled = 1
			doc.save(ignore_permissions=True)
			# 主客户继承源记录的关键联系信息（空字段才补）
			for f in ("email_id", "mobile_no", "territory", "customer_group"):
				if not keep_doc.get(f) and doc.get(f):
					keep_doc.set(f, doc.get(f))
		keep_doc.save(ignore_permissions=True)
	except Exception:
		frappe.db.rollback()
		raise
	from frappe.desk.form.utils import add_comment
	add_comment(
		"Customer", keep,
		"合并客户：{0}（保留主记录，源记录已停用）。".format("、".join(drops)),
		comment_email=frappe.session.user, comment_by=frappe.session.user,
	)
	frappe.db.commit()
	return {"keep": keep, "merged": drops}


def website_lead_rate_limit(doc, method=None):
	"""网站留言频控（T2-18）：同一 IP 每小时最多 5 条（Redis 计数），文案与实现一致。"""
	if not frappe.request:
		return
	ip = frappe.request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or frappe.request.remote_addr or "unknown"
	start = now_datetime().strftime("%Y%m%d%H")
	count_key = "lead_rl:" + ip + ":" + start
	try:
		c = frappe.cache().get_value(count_key)
		if c is None:
			frappe.cache().set_value(count_key, 1, expires_in_sec=3600)
		elif c >= 5:
			frappe.throw(_("提交过于频繁，请 1 小时后再试 / Too many submissions, try again later."), frappe.ValidationError)
		else:
			frappe.cache().set_value(count_key, c + 1, expires_in_sec=3600)
	except Exception:
		frappe.log_error(title="lead rate limit check failed")


@frappe.whitelist()
def share_customer(name, user, read=1, write=0):
	"""客户共享给指定同事（只读或共同负责）。"""
	_require_manager()
	doc = frappe.get_doc("Customer", name)
	doc.share(user, {"read": int(bool(read)), "write": int(bool(write))})
	frappe.db.commit()
	return True
