import csv
import io

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today


class StatisticsSettings(Document):
	"""统计设置：公海回收规则 + 报表订阅（定时邮件推送）+ 报表可见角色。"""


def get_pool_days():
	"""公海回收天数（默认 30 天）。"""
	d = frappe.db.get_single_value("Statistics Settings", "pool_days")
	return int(d) if d else 30


@frappe.whitelist()
def send_report_subscriptions():
	"""每日调度：按订阅频率/星期推送报表（CSV 附件邮件）。"""
	from frappe.core.doctype.report.report import get_report_module_dotted_path

	t = getdate(today())
	weekday = t.strftime("%A")
	sent = []
	subs = frappe.get_all(
		"Report Subscription",
		filters={"parenttype": "Statistics Settings"},
		fields=["report", "recipient", "frequency", "day_of_week"],
	)
	for s in subs:
		if not _today_matches(s, t, weekday):
			continue
		email = frappe.db.get_value("User", s.recipient, "email")
		if not email or not frappe.db.exists("Report", s.report):
			continue
		try:
			report_doc = frappe.get_doc("Report", s.report)
			path = get_report_module_dotted_path(report_doc.module, report_doc.name)
			columns, data = frappe.get_module(path).execute(frappe._dict({}))
			data = data or []
		except Exception:
			frappe.log_error(title=f"报表订阅推送失败：{s.report}")
			continue
		buf = io.StringIO()
		w = csv.writer(buf)
		w.writerow([c.get("label") if isinstance(c, dict) else str(c) for c in columns])
		for row in data:
			w.writerow(row if isinstance(row, (list, tuple)) else [row.get(c.get("fieldname")) if isinstance(c, dict) else row for c in columns])
		frappe.sendmail(
			recipients=[email],
			subject=f"报表订阅：{s.report}（{t}）",
			message=f"您订阅的报表「{s.report}」已生成，共 {len(data)} 行，详见附件。",
			attachments=[{"fname": f"{s.report}.csv", "fcontent": buf.getvalue()}],
		)
		sent.append(s.report)
	frappe.db.commit()
	return sent


def _today_matches(s, today, weekday):
	if s.frequency == "每日":
		return True
	if s.frequency == "每周":
		return s.day_of_week == weekday
	if s.frequency == "每月":
		return today.day == 1
	return False
