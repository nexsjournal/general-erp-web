frappe.ui.form.on('Trade Document', {
	refresh(frm) {
		frm.add_custom_button(__('一键出 PDF'), () => {
			frappe.call({
				method: 'general_erp.general_erp.doctype.trade_document.trade_document.generate_pdf',
				args: { name: frm.doc.name },
				freeze: true,
				freeze_message: __('正在生成 PDF…'),
				callback(r) {
					if (r.message) {
						frappe.msgprint(__('PDF 已生成：{0}', [r.message]), __('成功'));
						frm.reload_doc();
					}
				}
			});
		}, __('操作'));
	}
});
