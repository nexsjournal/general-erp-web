# -*- coding: utf-8 -*-
"""创建 PI（Proforma Invoice）中英对照打印格式，幂等"""
import frappe

PI_HTML = """
{%- set company = frappe.get_doc('Company', doc.company) if doc.company else {} -%}
{%- set terms_doc = frappe.get_doc('Incoterms', doc.trade_terms) if doc.trade_terms else None -%}
{%- set pol_doc = frappe.get_doc('Port', doc.port_of_loading) if doc.port_of_loading else None -%}
{%- set pod_doc = frappe.get_doc('Port', doc.port_of_discharge) if doc.port_of_discharge else None -%}
{%- set buyer = frappe.get_doc('Customer', doc.party_name) if doc.party_name else None -%}
<style>
	.pi { font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif; color: #1f2937; font-size: 12px; line-height: 1.55; }
	.pi * { box-sizing: border-box; }
	.pi-header { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #0289F7; padding-bottom: 12px; }
	.pi-company { font-size: 18px; font-weight: 700; letter-spacing: .5px; }
	.pi-company-sub { color: #6b7280; font-size: 11px; margin-top: 2px; }
	.pi-title { font-size: 20px; font-weight: 700; letter-spacing: 2px; }
	.pi-title-sub { color: #6b7280; font-size: 11px; text-align: right; }
	.pi-meta { margin-top: 10px; display: flex; gap: 40px; }
	.pi-meta div span { display: block; color: #6b7280; font-size: 10px; }
	.pi-parties { display: flex; gap: 32px; margin-top: 14px; }
	.pi-party { flex: 1; background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 8px; padding: 10px 12px; }
	.pi-party h4 { margin: 0 0 6px; font-size: 10px; color: #0289F7; letter-spacing: 1px; }
	.pi-party p { margin: 0; white-space: pre-line; }
	.pi-terms { margin-top: 14px; }
	.pi-terms table { width: 100%; border-collapse: collapse; }
	.pi-terms td { border: 1px solid #e5e7eb; padding: 6px 10px; }
	.pi-terms td.k { background: #f8fafc; color: #6b7280; width: 110px; }
	.pi-items { margin-top: 14px; }
	.pi-items table { width: 100%; border-collapse: collapse; }
	.pi-items th { background: #0289F7; color: #fff; text-align: left; padding: 7px 10px; font-size: 11px; }
	.pi-items td { border-bottom: 1px solid #e5e7eb; padding: 7px 10px; }
	.pi-items .num { text-align: right; }
	.pi-totals { margin-top: 10px; margin-left: auto; width: 320px; }
	.pi-totals table { width: 100%; border-collapse: collapse; }
	.pi-totals td { padding: 5px 10px; }
	.pi-totals td.k { color: #6b7280; }
	.pi-totals td.v { text-align: right; font-weight: 600; }
	.pi-totals tr.grand td { border-top: 2px solid #0289F7; font-size: 13px; font-weight: 700; }
	.pi-words { margin-top: 10px; background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 8px; padding: 8px 12px; }
	.pi-words .en { color: #6b7280; font-size: 10px; margin-top: 2px; }
	.pi-footer { display: flex; justify-content: space-between; margin-top: 40px; }
	.pi-sign { width: 40%; border-top: 1px solid #9ca3af; padding-top: 6px; color: #6b7280; font-size: 11px; }
</style>
<div class="pi">
	<div class="pi-header">
		<div>
			<div class="pi-company">{{ company.get("company_name") or doc.company }}</div>
			{% if company.get("english_name") %}<div class="pi-company-sub">{{ company.get("english_name") }}</div>{% endif %}
		</div>
		<div>
			<div class="pi-title">PROFORMA INVOICE</div>
			<div class="pi-title-sub">形式发票</div>
		</div>
	</div>

	<div class="pi-meta">
		<div><span>PI 编号 / Invoice No.</span>{{ doc.name }}</div>
		<div><span>日期 / Date</span>{{ frappe.utils.formatdate(doc.transaction_date, "yyyy-MM-dd") }}</div>
		<div><span>有效期至 / Valid Till</span>{{ frappe.utils.formatdate(doc.valid_till, "yyyy-MM-dd") if doc.valid_till else "" }}</div>
	</div>

	<div class="pi-parties">
		<div class="pi-party">
			<h4>卖方 SELLER</h4>
			<p>{{ company.get("company_name") or "" }}
{% if company.get("english_name") %}{{ company.get("english_name") }}{% endif %}
{% if company.get("address_display") %}{{ company.get("address_display") }}{% endif %}
{% if company.get("phone_no") %}Tel: {{ company.get("phone_no") }}{% endif %}</p>
		</div>
		<div class="pi-party">
			<h4>买方 BUYER</h4>
			<p>{% if buyer %}{{ buyer.get("customer_name") }}
{% if doc.customer_address %}{{ doc.customer_address }}{% endif %}{% else %}{{ doc.party_name or "" }}{% endif %}</p>
		</div>
	</div>

	<div class="pi-terms">
		<table>
			<tr>
				<td class="k">贸易术语 Terms</td>
				<td>{% if terms_doc %}{{ terms_doc.get("code") }} {{ terms_doc.get("chinese_name") }}{% if terms_doc.get("english_name") %} / {{ terms_doc.get("english_name") }}{% endif %}{% else %}—{% endif %}</td>
				<td class="k">装运港 Port of Loading</td>
				<td>{% if pol_doc %}{{ pol_doc.get("port_name") }} ({{ pol_doc.get("code") }}){% else %}—{% endif %}</td>
			</tr>
			<tr>
				<td class="k">目的港 Port of Discharge</td>
				<td>{% if pod_doc %}{{ pod_doc.get("port_name") }} ({{ pod_doc.get("code") }}){% else %}—{% endif %}</td>
				<td class="k">货币 Currency</td>
				<td>{{ doc.currency }}</td>
			</tr>
		</table>
	</div>

	<div class="pi-items">
		<table>
			<thead>
				<tr>
					<th style="width:36px">#</th>
					<th>品名 Description</th>
					<th class="num">数量 Qty</th>
					<th>单位 UOM</th>
					<th class="num">单价 Unit Price</th>
					<th class="num">金额 Amount</th>
				</tr>
			</thead>
			<tbody>
				{% for item in doc.items %}
				<tr>
					<td>{{ loop.index }}</td>
					<td>{{ item.item_name }}{% if item.description %} — {{ item.description }}{% endif %}</td>
					<td class="num">{{ item.qty }}</td>
					<td>{{ item.uom }}</td>
					<td class="num">{{ frappe.utils.fmt_money(item.rate, currency=doc.currency) }}</td>
					<td class="num">{{ frappe.utils.fmt_money(item.amount, currency=doc.currency) }}</td>
				</tr>
				{% endfor %}
			</tbody>
		</table>
	</div>

	<div class="pi-totals">
		<table>
			<tr><td class="k">合计 Total</td><td class="v">{{ frappe.utils.fmt_money(doc.grand_total, currency=doc.currency) }}</td></tr>
			{% if doc.discount_amount %}<tr><td class="k">折扣 Discount</td><td class="v">-{{ frappe.utils.fmt_money(doc.discount_amount, currency=doc.currency) }}</td></tr>{% endif %}
			<tr class="grand"><td class="k">总计 Grand Total</td><td class="v">{{ frappe.utils.fmt_money(doc.base_grand_total, currency=doc.base_currency) if doc.base_currency else frappe.utils.fmt_money(doc.grand_total, currency=doc.currency) }}</td></tr>
		</table>
	</div>

	<div class="pi-words">
		金额大写 In Words: {{ money_in_words_cn(doc.grand_total or 0, doc.currency or "CNY") }}
	</div>

	<div class="pi-footer">
		<div class="pi-sign">卖方盖章 / Seller (Signature & Stamp)</div>
		<div class="pi-sign">买方确认 / Buyer (Signature & Stamp)</div>
	</div>
</div>
"""


def execute():
	if not frappe.db.exists("Print Format", "PI 中英对照"):
		frappe.get_doc(
			{
				"doctype": "Print Format",
				"name": "PI 中英对照",
				"doc_type": "Quotation",
				"module": "General ERP",
				"standard": "No",
				"print_format_type": "Jinja",
				"custom_format": 1,
				"html": PI_HTML,
			}
		).insert(ignore_permissions=True)
		frappe.db.commit()
	else:
		doc = frappe.get_doc("Print Format", "PI 中英对照")
		needs = doc.html != PI_HTML or not doc.custom_format
		if needs:
			doc.html = PI_HTML
			doc.custom_format = 1
			doc.save(ignore_permissions=True)
			frappe.db.commit()
