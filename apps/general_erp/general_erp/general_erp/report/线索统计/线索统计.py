# -*- coding: utf-8 -*-
import frappe
from frappe import _


def execute(filters=None):
	"""线索按被分发人统计：数量、已转化、转化率。"""
	filters = frappe._dict(filters or {})
	status_filter = "AND l.status = %(status)s" if filters.get("status") else ""
	rows = frappe.db.sql(
		"""SELECT coalesce(l.assigned_to, '（未分发）') AS owner, count(*) AS total,
			sum(case when l.status = 'Converted' then 1 else 0 end) AS converted
		FROM `tabLead` l WHERE l.docstatus = 0 {sf}
		GROUP BY owner ORDER BY total DESC""".format(sf=status_filter),
		{"status": filters.get("status")}, as_dict=True)
	data = []
	for r in rows:
		rate = round(r.converted * 100.0 / r.total, 1) if r.total else 0
		data.append({"owner": r.owner, "total": r.total, "converted": r.converted or 0, "rate": str(rate) + "%"})
	columns = [
		{"label": _("被分发人"), "fieldname": "owner", "fieldtype": "Data"},
		{"label": _("线索数"), "fieldname": "total", "fieldtype": "Int"},
		{"label": _("已转化"), "fieldname": "converted", "fieldtype": "Int"},
		{"label": _("转化率"), "fieldname": "rate", "fieldtype": "Data"},
	]
	return columns, data
