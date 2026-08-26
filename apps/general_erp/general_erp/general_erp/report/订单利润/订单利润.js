frappe.query_reports["订单利润"] = {
	filters: [
		{ fieldname: "from_date", label: __("开始日期"), fieldtype: "Date", default: frappe.datetime.get_today().slice(0, 8) + "01" },
		{ fieldname: "to_date", label: __("结束日期"), fieldtype: "Date", default: frappe.datetime.get_today() },
		{ fieldname: "customer", label: __("客户"), fieldtype: "Link", options: "Customer" },
	],
	}
