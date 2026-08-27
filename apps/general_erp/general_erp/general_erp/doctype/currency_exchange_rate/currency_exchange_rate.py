import frappe

from frappe.model.document import Document
from frappe.utils import today


class CurrencyExchangeRate(Document):
	"""币种汇率：工作台「今日汇率」数字卡的数据源。"""


@frappe.whitelist()
def get_today_rate():
	"""取今日最新一条汇率（无则返回 None），供工作台数字卡（type=Custom）调用。"""
	rate = frappe.db.sql(
		"select rate from `tabCurrency Exchange Rate` where date = %(date)s order by creation desc limit 1",
		{"date": today()},
		pluck=True,
	)
	return {"value": rate[0] if rate else None}
