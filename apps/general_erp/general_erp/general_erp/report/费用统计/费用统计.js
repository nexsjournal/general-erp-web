frappe.query_reports["费用统计"] = {
	filters: [
		{ fieldname: "from_date", label: __("开始日期"), fieldtype: "Date", default: frappe.datetime.get_today().slice(0, 8) + "01" },
		{ fieldname: "to_date", label: __("结束日期"), fieldtype: "Date", default: frappe.datetime.get_today() },
		{ fieldname: "group_by", label: __("按"), fieldtype: "Select", options: "月份\n费用类型\n申请人", default: "月份" },
	],
	}
