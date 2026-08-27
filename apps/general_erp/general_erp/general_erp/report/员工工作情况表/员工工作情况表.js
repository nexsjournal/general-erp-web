frappe.query_reports["员工工作情况表"] = {
	filters: [
		{ fieldname: "from_date", label: "开始日期", fieldtype: "Date", default: frappe.datetime.add_months(frappe.datetime.nowdate(), -1) },
		{ fieldname: "to_date", label: "结束日期", fieldtype: "Date", default: frappe.datetime.nowdate() },
	],
};
