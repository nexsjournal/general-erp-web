frappe.query_reports["付款统计"] = {
	filters: [
		{ fieldname: "from_date", label: __("开始日期"), fieldtype: "Date", default: frappe.datetime.get_today().slice(0, 8) + "01" },
		{ fieldname: "to_date", label: __("结束日期"), fieldtype: "Date", default: frappe.datetime.get_today() },
		{ fieldname: "group_by", label: __("按"), fieldtype: "Select", options: "月份\n供应商\n制单人", default: "月份" },
		{ fieldname: "supplier", label: __("供应商"), fieldtype: "Link", options: "Supplier" },
	],
	}
