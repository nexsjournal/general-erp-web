# -*- coding: utf-8 -*-
"""创建 CI/PL/BL 中英对照打印格式，幂等"""
import frappe

BASE_CSS = """
	.pi { font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif; color: #1f2937; font-size: 12px; line-height: 1.55; }
	.pi * { box-sizing: border-box; }
	.pi-header { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #0289F7; padding-bottom: 12px; }
	.pi-company { font-size: 18px; font-weight: 700; letter-spacing: .5px; }
	.pi-company-sub { color: #6b7280; font-size: 11px; margin-top: 2px; }
	.pi-title { font-size: 20px; font-weight: 700; letter-spacing: 2px; }
	.pi-title-sub { color: #6b7280; font-size: 11px; text-align: right; }
	.pi-meta { margin-top: 10px; display: flex; flex-wrap: wrap; gap: 40px; }
	.pi-meta div span { display: block; color: #6b7280; font-size: 10px; }
	.pi-parties { display: flex; gap: 32px; margin-top: 14px; }
	.pi-party { flex: 1; background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 8px; padding: 10px 12px; }
	.pi-party h4 { margin: 0 0 6px; font-size: 10px; color: #0289F7; letter-spacing: 1px; }
	.pi-party p { margin: 0; white-space: pre-line; }
	.pi-terms { margin-top: 14px; }
	.pi-terms table { width: 100%; border-collapse: collapse; }
	.pi-terms td { border: 1px solid #e5e7eb; padding: 6px 10px; }
	.pi-terms td.k { background: #f8fafc; color: #6b7280; width: 130px; }
	.pi-items { margin-top: 14px; }
	.pi-items table { width: 100%; border-collapse: collapse; }
	.pi-items th { background: #0289F7; color: #fff; text-align: left; padding: 7px 10px; font-size: 11px; }
	.pi-items td { border-bottom: 1px solid #e5e7eb; padding: 7px 10px; }
	.pi-items .num { text-align: right; }
	.pi-items tr.sum td { border-top: 2px solid #0289F7; font-weight: 700; background: #f8fafc; }
	.pi-totals { margin-top: 10px; margin-left: auto; width: 320px; }
	.pi-totals table { width: 100%; border-collapse: collapse; }
	.pi-totals td { padding: 5px 10px; }
	.pi-totals td.k { color: #6b7280; }
	.pi-totals td.v { text-align: right; font-weight: 600; }
	.pi-totals tr.grand td { border-top: 2px solid #0289F7; font-size: 13px; font-weight: 700; }
	.pi-words { margin-top: 10px; background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 8px; padding: 8px 12px; }
	.pi-footer { display: flex; justify-content: space-between; margin-top: 40px; }
	.pi-sign { width: 40%; border-top: 1px solid #9ca3af; padding-top: 6px; color: #6b7280; font-size: 11px; }
"""

HEADER_SETS = """
{%- set co_name = doc.company or frappe.db.get_default("company") -%}
{%- set company = frappe.get_doc('Company', co_name) if co_name else {} -%}
"""

HEADER_HTML = """
	<div class="pi-header">
		<div>
			<div class="pi-company">{{ company.get("company_name") or co_name }}</div>
			{% if company.get("english_name") %}<div class="pi-company-sub">{{ company.get("english_name") }}</div>{% endif %}
		</div>
		<div>
			<div class="pi-title">{{ TITLE_EN }}</div>
			<div class="pi-title-sub">{{ TITLE_CN }}</div>
		</div>
	</div>
"""

FOOTER_HTML = """
	<div class="pi-footer">
		<div class="pi-sign">卖方盖章 / Seller (Signature &amp; Stamp)</div>
		<div class="pi-sign">买方确认 / Buyer (Signature &amp; Stamp)</div>
	</div>
"""

CI_HTML = HEADER_SETS + """
{%- set terms_doc = frappe.get_doc('Incoterms', doc.trade_terms) if doc.trade_terms else None -%}
{%- set pol_doc = frappe.get_doc('Port', doc.port_of_loading) if doc.port_of_loading else None -%}
{%- set pod_doc = frappe.get_doc('Port', doc.port_of_discharge) if doc.port_of_discharge else None -%}
{%- set buyer = frappe.get_doc('Customer', doc.customer) if doc.customer else None -%}
<style>""" + BASE_CSS + """</style>
<div class="pi">
""" + HEADER_HTML.replace("{{ TITLE_EN }}", "COMMERCIAL INVOICE").replace("{{ TITLE_CN }}", "商业发票") + """
	<div class="pi-meta">
		<div><span>发票编号 / Invoice No.</span>{{ doc.name }}</div>
		<div><span>日期 / Date</span>{{ frappe.utils.formatdate(doc.transaction_date, "yyyy-MM-dd") }}</div>
		<div><span>预计出运 / Planned Shipment</span>{{ frappe.utils.formatdate(doc.planned_ship_date, "yyyy-MM-dd") if doc.planned_ship_date else "" }}</div>
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
{% if doc.customer_address %}{{ doc.customer_address }}{% endif %}{% else %}{{ doc.customer or "" }}{% endif %}</p>
		</div>
	</div>

	<div class="pi-terms">
		<table>
			<tr>
				<td class="k">贸易术语 Trade Terms</td>
				<td>{% if terms_doc %}{{ terms_doc.get("code") }} {{ terms_doc.get("chinese_name") }}{% if terms_doc.get("english_name") %} / {{ terms_doc.get("english_name") }}{% endif %}{% else %}—{% endif %}</td>
				<td class="k">装运港 Port of Loading</td>
				<td>{% if pol_doc %}{{ pol_doc.get("port_name") }} ({{ pol_doc.get("code") }}){% else %}—{% endif %}</td>
			</tr>
			<tr>
				<td class="k">目的港 Port of Destination</td>
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
			<tr class="grand"><td class="k">总计 Total</td><td class="v">{{ frappe.utils.fmt_money(doc.grand_total, currency=doc.currency) }}</td></tr>
		</table>
	</div>

	<div class="pi-words">
		金额大写 In Words: {{ money_in_words_cn(doc.grand_total or 0, doc.currency or "CNY") }}
	</div>
""" + FOOTER_HTML + """
</div>
"""

SHIPMENT_SETS = """
{%- set co_name = doc.company or frappe.db.get_default("company") -%}
{%- set company = frappe.get_doc('Company', co_name) if co_name else {} -%}
{%- set buyer = frappe.get_doc('Customer', doc.customer) if doc.customer else None -%}
{%- set pol_doc = frappe.get_doc('Port', doc.port_of_loading) if doc.port_of_loading else None -%}
{%- set pod_doc = frappe.get_doc('Port', doc.port_of_discharge) if doc.port_of_discharge else None -%}
{%- set terms_doc = frappe.get_doc('Incoterms', doc.incoterms) if doc.incoterms else None -%}
{%- set gw = doc.items|sum(attribute='gross_weight') or 0 -%}
{%- set nw = doc.items|sum(attribute='net_weight') or 0 -%}
{%- set vol = doc.items|sum(attribute='volume') or 0 -%}
{%- set qty = doc.items|sum(attribute='qty') or 0 -%}
"""

SHIPMENT_ITEMS_TABLE = """
	<div class="pi-items">
		<table>
			<thead>
				<tr>
					<th style="width:36px">#</th>
					<th>品名 Description</th>
					<th class="num">数量 Qty</th>
					<th>单位 UOM</th>
					<th>包装 Packing</th>
					<th class="num">毛重 GW (kg)</th>
					<th class="num">净重 NW (kg)</th>
					<th class="num">体积 CBM</th>
					<th>备注 Remark</th>
				</tr>
			</thead>
			<tbody>
				{% for item in doc.items %}
				<tr>
					<td>{{ loop.index }}</td>
					<td>{{ item.item_name }}{% if item.item_code %} <span style="color:#6b7280">({{ item.item_code }})</span>{% endif %}</td>
					<td class="num">{{ item.qty }}</td>
					<td>{{ item.uom }}</td>
					<td>{{ item.packing or "" }}</td>
					<td class="num">{{ item.gross_weight or 0 }}</td>
					<td class="num">{{ item.net_weight or 0 }}</td>
					<td class="num">{{ item.volume or 0 }}</td>
					<td>{{ item.remark or "" }}</td>
				</tr>
				{% endfor %}
				<tr class="sum">
					<td colspan="2">合计 Total</td>
					<td class="num">{{ qty }}</td>
					<td></td>
					<td></td>
					<td class="num">{{ gw }}</td>
					<td class="num">{{ nw }}</td>
					<td class="num">{{ vol }}</td>
					<td></td>
				</tr>
			</tbody>
		</table>
	</div>
"""

SHIPMENT_INFO_TABLE = """
	<div class="pi-terms">
		<table>
			<tr>
				<td class="k">装运港 POL</td>
				<td>{% if pol_doc %}{{ pol_doc.get("port_name") }}{% if pol_doc.get("code") %} ({{ pol_doc.get("code") }}){% endif %}{% else %}—{% endif %}</td>
				<td class="k">目的港 POD</td>
				<td>{% if pod_doc %}{{ pod_doc.get("port_name") }}{% if pod_doc.get("code") %} ({{ pod_doc.get("code") }}){% endif %}{% else %}—{% endif %}</td>
			</tr>
			<tr>
				<td class="k">运输方式 Transport</td>
				<td>{{ doc.transport_mode or "" }}</td>
				<td class="k">船名/航次 Vessel/Voyage</td>
				<td>{{ doc.vessel_voyage or "" }}</td>
			</tr>
			<tr>
				<td class="k">集装箱号 Container No.</td>
				<td>{{ doc.container_no or "" }}</td>
				<td class="k">贸易术语 Trade Terms</td>
				<td>{% if terms_doc %}{{ terms_doc.get("code") }}{% else %}—{% endif %}</td>
			</tr>
			<tr>
				<td class="k">预计开航 ETD</td>
				<td>{{ frappe.utils.formatdate(doc.etd, "yyyy-MM-dd") if doc.etd else "" }}</td>
				<td class="k">预计到港 ETA</td>
				<td>{{ frappe.utils.formatdate(doc.eta, "yyyy-MM-dd") if doc.eta else "" }}</td>
			</tr>
		</table>
	</div>
"""

PL_HTML = SHIPMENT_SETS + """
<style>""" + BASE_CSS + """</style>
<div class="pi">
""" + HEADER_HTML.replace("{{ TITLE_EN }}", "PACKING LIST").replace("{{ TITLE_CN }}", "装箱单") + """
	<div class="pi-meta">
		<div><span>单号 / No.</span>{{ doc.name }}</div>
		<div><span>提单号 / B/L No.</span>{{ doc.bl_no or "" }}</div>
		<div><span>客户 Customer</span>{{ doc.customer or "" }}</div>
		<div><span>销售订单 / Sales Order</span>{{ doc.sales_order or "" }}</div>
	</div>
""" + SHIPMENT_INFO_TABLE + SHIPMENT_ITEMS_TABLE + """
	<div class="pi-words">
		总毛重 Total GW: {{ gw }} kg &nbsp;&nbsp; 总净重 Total NW: {{ nw }} kg &nbsp;&nbsp; 总体积 Total Volume: {{ vol }} CBM
	</div>
""" + FOOTER_HTML + """
</div>
"""

BL_HTML = SHIPMENT_SETS + """
<style>""" + BASE_CSS + """</style>
<div class="pi">
""" + HEADER_HTML.replace("{{ TITLE_EN }}", "BILL OF LADING (COPY)").replace("{{ TITLE_CN }}", "提单（副本）") + """
	<div class="pi-meta">
		<div><span>提单号 / B/L No.</span>{{ doc.bl_no or doc.name }}</div>
		<div><span>出运单号 / Shipment No.</span>{{ doc.name }}</div>
		<div><span>集装箱号 / Container No.</span>{{ doc.container_no or "" }}</div>
	</div>

	<div class="pi-parties">
		<div class="pi-party">
			<h4>发货人 SHIPPER</h4>
			<p>{{ company.get("company_name") or "" }}
{% if company.get("english_name") %}{{ company.get("english_name") }}{% endif %}
{% if company.get("address_display") %}{{ company.get("address_display") }}{% endif %}</p>
		</div>
		<div class="pi-party">
			<h4>收货人 CONSIGNEE</h4>
			<p>{% if buyer %}{{ buyer.get("customer_name") }}{% else %}{{ doc.customer or "" }}{% endif %}
TO ORDER OF ISSUING BANK</p>
		</div>
		<div class="pi-party">
			<h4>通知方 NOTIFY PARTY</h4>
			<p>{% if buyer %}{{ buyer.get("customer_name") }}{% else %}{{ doc.customer or "" }}{% endif %}
{% if doc.customer_address or (buyer and buyer.get("address_display")) %}{{ doc.customer_address or (buyer.get("address_display") if buyer else "") }}{% endif %}</p>
		</div>
	</div>
""" + SHIPMENT_INFO_TABLE + """
	<div class="pi-items">
		<table>
			<thead>
				<tr>
					<th style="width:36px">#</th>
					<th>唛头 Marks &amp; Nos.</th>
					<th>货描 Description of Goods</th>
					<th class="num">件数 Pkgs</th>
					<th class="num">毛重 GW (kg)</th>
					<th class="num">体积 CBM</th>
				</tr>
			</thead>
			<tbody>
				{% for item in doc.items %}
				<tr>
					<td>{{ loop.index }}</td>
					<td>{{ doc.container_no or "N/M" }}</td>
					<td>{{ item.item_name }}{% if item.description %} — {{ item.description }}{% endif %}</td>
					<td class="num">{{ item.qty }}</td>
					<td class="num">{{ item.gross_weight or 0 }}</td>
					<td class="num">{{ item.volume or 0 }}</td>
				</tr>
				{% endfor %}
				<tr class="sum">
					<td colspan="3">合计 Total</td>
					<td class="num">{{ qty }}</td>
					<td class="num">{{ gw }}</td>
					<td class="num">{{ vol }}</td>
				</tr>
			</tbody>
		</table>
	</div>

	<div class="pi-words">
		托运人声明 Shipper's Declaration: We hereby declare that the whole of the above particulars, statements and declarations are true and correct.
	</div>
	<div class="pi-footer">
		<div class="pi-sign">承运人签章 / Signed for the Carrier</div>
		<div class="pi-sign">提单日期 / Date of Issue: {{ frappe.utils.formatdate(doc.etd, "yyyy-MM-dd") if doc.etd else "" }}</div>
	</div>
</div>
"""

FORMATS = [
    ("CI 商业发票 中英对照", "Sales Order", CI_HTML),
    ("PL 装箱单 中英对照", "Shipment", PL_HTML),
    ("BL 提单副本 中英对照", "Shipment", BL_HTML),
]


def execute():
	for name, doc_type, html in FORMATS:
		if not frappe.db.exists("Print Format", name):
			frappe.get_doc(
				{
					"doctype": "Print Format",
					"name": name,
					"doc_type": doc_type,
					"module": "General ERP",
					"standard": "No",
					"print_format_type": "Jinja",
					"custom_format": 1,
					"html": html,
				}
			).insert(ignore_permissions=True)
			print("created", name)
		else:
			doc = frappe.get_doc("Print Format", name)
			if doc.html != html or not doc.custom_format:
				doc.html = html
				doc.custom_format = 1
				doc.save(ignore_permissions=True)
				print("updated", name)
	frappe.db.commit()
