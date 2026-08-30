from frappe import _
import frappe
from frappe.model.document import Document

FORMAT_MAP = {
	'PI 形式发票': 'PI 形式发票 中英对照',
	'CI 商业发票': 'CI 商业发票 中英对照',
	'PL 装箱单': 'PL 装箱单 中英对照',
	'BL 提单': 'BL 提单副本 中英对照',
}


class TradeDocument(Document):
	pass


def _resolve_target(doc):
	doc_type = (doc.doc_type or '').strip()
	if doc_type not in FORMAT_MAP:
		frappe.throw(_('单证类型 {0} 暂不支持一键出单，请手工打印').format(doc_type), frappe.ValidationError)
	print_format = FORMAT_MAP[doc_type]
	if not frappe.db.exists('Print Format', print_format):
		frappe.throw(_('打印格式 {0} 不存在，请先执行 migrate').format(print_format), frappe.ValidationError)
	if doc_type in ('PI 形式发票', 'CI 商业发票'):
		if not doc.sales_order:
			frappe.throw(_('请先选择关联销售订单'), frappe.ValidationError)
		return 'Sales Order', doc.sales_order, print_format
	if not doc.shipment:
		frappe.throw(_('请先选择关联出运单'), frappe.ValidationError)
	return 'Export Shipment', doc.shipment, print_format


def _render_print_html(print_format, target):
	pf = frappe.get_doc('Print Format', print_format)
	body = frappe.render_template(pf.html, {'doc': target, 'frm': target})
	return ('<!DOCTYPE html><html><head><meta charset=utf-8><style>'
		+ (pf.css or '')
		+ '</style></head><body><div class=print-format>'
		+ body
		+ '</div></body></html>')


@frappe.whitelist()
def generate_pdf(name):
	"""一键出 PDF：按单证类型定位目标单据与打印格式，weasyprint 渲染落盘，回写 status=已生成。"""
	doc = frappe.get_doc('Trade Document', name)
	doctype, target_name, print_format = _resolve_target(doc)
	target = frappe.get_doc(doctype, target_name)
	html = _render_print_html(print_format, target)
	try:
		from weasyprint import HTML as WeasyHTML
		pdf_bytes = WeasyHTML(string=html, base_url=frappe.utils.get_url()).write_pdf()
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), 'TradeDocument generate_pdf')
		frappe.throw(_('PDF 生成失败：{0}').format(str(e)[:150]), frappe.ValidationError)
	if not pdf_bytes or len(pdf_bytes) < 100:
		frappe.throw(_('PDF 内容为空，生成失败'), frappe.ValidationError)
	file_name = '{0}_{1}.pdf'.format(doc.name, print_format[:8].replace(' ', ''))
	file_doc = frappe.get_doc({
		'doctype': 'File',
		'file_name': file_name,
		'content': pdf_bytes,
		'attached_to_doctype': 'Trade Document',
		'attached_to_name': doc.name,
		'is_private': 0,
	})
	file_doc.save(ignore_permissions=True)
	doc.status = '已生成'
	doc.generated_on = frappe.utils.nowdate()
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return file_doc.file_url
