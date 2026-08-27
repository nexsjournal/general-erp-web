frappe.query_reports["出运统计"] = {
	filters: [
		{ fieldname: "from_date", label: "开始日期", fieldtype: "Date", reqd: 0 },
		{ fieldname: "to_date", label: "结束日期", fieldtype: "Date", reqd: 0 },
		{
			fieldname: "group_by",
			label: "分组",
			fieldtype: "Select",
			options: "月份\n目的港\n客户",
			default: "月份",
		},
		{ fieldname: "customer", label: "客户", fieldtype: "Link", options: "Customer" },
	],
};
