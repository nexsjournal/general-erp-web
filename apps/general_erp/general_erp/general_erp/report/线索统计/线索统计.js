frappe.query_reports["线索统计"] = {
	filters: [
		{ fieldname: "status", label: "线索状态", fieldtype: "Select", options: "Lead\nOpen\nReplied\nOpportunity\nQuotation\nLost Quotation\nInterested\nConverted\nDo Not Contact" },
	],
};
