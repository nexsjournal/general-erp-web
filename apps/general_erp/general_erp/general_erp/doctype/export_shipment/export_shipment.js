frappe.ui.form.on('Export Shipment', {
	refresh(frm) {
		if (!frm.doc.__islocal && !frm.is_new()) {
			frm.add_custom_button(__('从订单生成'), () => {
				frappe.prompt({
					label: __('销售订单'),
					fieldname: 'sales_order',
					fieldtype: 'Link',
					options: 'Sales Order',
					reqd: 1
				}, (values) => {
					frappe.call({
						method: 'general_erp.general_erp.doctype.export_shipment.export_shipment.make_shipment_from_sales_order',
						args: { sales_order_name: values.sales_order },
						freeze: true,
						callback(r) {
							if (r.message) {
								frappe.msgprint(__('已生成出运单 {0}', [r.message]), __('成功'));
								frappe.set_route('List', 'Export Shipment', { name: ['like', r.message] });
							}
						}
					});
				}).toggle(true);
			}, __('创建'));
		}
	}
});
