frappe.query_reports["产品统计"] = {
	filters: [
		{ fieldname: "from_date", label: __("开始日期"), fieldtype: "Date", default: frappe.datetime.get_today().slice(0, 8) + "01" },
		{ fieldname: "to_date", label: __("结束日期"), fieldtype: "Date", default: frappe.datetime.get_today() },
		{ fieldname: "group_by", label: __("按"), fieldtype: "Select", options: "月份\n商品", default: "月份" },
		{ fieldname: "item", label: __("商品"), fieldtype: "Link", options: "Item" },
	],
	}
