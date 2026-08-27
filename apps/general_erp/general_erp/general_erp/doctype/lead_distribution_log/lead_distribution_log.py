import frappe

from frappe.model.document import Document


class LeadDistributionLog(Document):
	"""线索分发记录：线索在员工间分发的留痕。"""


@frappe.whitelist()
def assign_lead(name, to_user, remark=None):
	"""分派线索：更新线索的被分发人并写入分发记录。"""
	from frappe.utils import now_datetime
	lead = frappe.get_doc("Lead", name)
	lead.assigned_to = to_user
	lead.assigned_at = now_datetime()
	lead.flags.ignore_permissions = True
	lead.save()
	log = frappe.new_doc("Lead Distribution Log")
	log.update({
		"lead": name,
		"lead_name": lead.lead_name,
		"from_user": frappe.session.user,
		"to_user": to_user,
		"remark": remark or None,
		"distributed_at": now_datetime(),
	})
	log.insert(ignore_permissions=True)
	frappe.db.commit()
	return log.name
