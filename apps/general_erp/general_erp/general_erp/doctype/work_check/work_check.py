import frappe

from frappe.model.document import Document
from frappe.utils import now_datetime, nowdate


class WorkCheck(Document):
	"""工作检查：周期性检查任务，主管布置、员工完成并反馈。"""

	def validate(self):
		if self.status == "已完成" and not self.completed_at:
			self.completed_at = now_datetime()
		if self.status != "已完成" and self.completed_at:
			self.completed_at = None


@frappe.whitelist()
def complete_check(name):
	"""完成检查：全部检查项标记完成并填写反馈。"""
	doc = frappe.get_doc("Work Check", name)
	for item in doc.items:
		item.done = 1
	doc.status = "已完成"
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return doc.name


@frappe.whitelist()
def remind_work_checks():
	"""每日调度：检查日当天仍待检查的任务，给被检查人发待办。"""
	today = nowdate()
	rows = frappe.get_all("Work Check", filters={"status": "待检查", "check_date": today}, fields=["name", "title", "assignee"])
	created = []
	for r in rows:
		exists = frappe.db.exists("ToDo", {"reference_type": "Work Check", "reference_name": r.name, "allocated_to": r.assignee})
		if not exists and r.assignee:
			t = frappe.new_doc("ToDo")
			t.update({"title": f"工作检查：{r.title}", "description": f"请完成今日工作检查「{r.title}」并填写结果。", "reference_type": "Work Check", "reference_name": r.name, "allocated_to": r.assignee})
			t.insert(ignore_permissions=True)
			created.append(t.name)
	frappe.db.commit()
	return created
