frappe.query_reports["收款统计"] = {
	filters: [
		{ fieldname: "from_date", label: __("开始日期"), fieldtype: "Date", default: frappe.datetime.get_today().slice(0, 8) + "01" },
		{ fieldname: "to_date", label: __("结束日期"), fieldtype: "Date", default: frappe.datetime.get_today() },
		{ fieldname: "group_by", label: __("按"), fieldtype: "Select", options: "月份\n客户\n制单人", default: "月份" },
		{ fieldname: "customer", label: __("客户"), fieldtype: "Link", options: "Customer" },
	],
	}
