/* 客户 360：基本信息 + 跟进时间线 + 商机 + 报价 + 订单 + 邮件，支持共享 / 合并 / 移交 */

const C360 = {
	customer: null,

	async load() {
		const q = new URLSearchParams(location.search).get('customer');
		this.customer = q || (frappe.route_options && frappe.route_options.customer) || null;
		if (this.customer) this.render();
	},

	async render() {
		const c = this.customer;
		const wrap = document.querySelector('.c360-main');
		wrap.innerHTML = `<div class="c360-loading">${__('加载中…')}</div>`;
		const doc = await frappe.db.get_doc('Customer', c).catch(() => null);
		if (!doc) { wrap.innerHTML = `<div class="c360-loading">${__('客户不存在或无权查看')}</div>`; return; }
		const stats = await Promise.all([
			frappe.db.get_list('Customer Follow Up', { filters: { customer: c }, fields: ['name', 'follow_type', 'follow_date', 'content', 'next_follow_date', 'followed_by'], order_by: 'follow_date desc', limit: 30 }),
			frappe.db.get_list('Opportunity', { filters: { customer_name: c }, fields: ['name', 'title', 'status', 'opportunity_amount', 'currency', 'review_status'], limit: 20 }),
			frappe.db.get_list('Quotation', { filters: { customer_name: c }, fields: ['name', 'transaction_date', 'grand_total', 'currency', 'status'], limit: 20 }),
			frappe.db.get_list('Sales Order', { filters: { customer: c }, fields: ['name', 'transaction_date', 'grand_total', 'currency', 'status'], limit: 20 }),
			frappe.db.get_list('Mail', { filters: { related_doctype: 'Customer', related_name: c }, fields: ['name', 'subject', 'folder', 'sent_at'], order_by: 'sent_at desc', limit: 20 }),
		]);
		[doc.follows, doc.opps, doc.quots, doc.orders, doc.mails] = stats;
		const owner = doc.sales_owner ? ((frappe.user_info[doc.sales_owner] && frappe.user_info[doc.sales_owner].full_name) || doc.sales_owner) : '—';
		const acts = document.querySelector('.c360-actions');
		if (acts) acts.style.visibility = 'visible';
		const so_total = doc.orders.reduce((a, b) => a + (b.grand_total || 0), 0);

		wrap.innerHTML = `
			${doc.merged_into ? `<div class="c360-banner">⚠ ${__("该客户已合并至")} <b>${doc.merged_into}</b>，${__("业务数据以主记录为准")}</div>` : ''}
			<div class="c360-info card">
				<div class="c360-info-head">
					<div>
						<div class="c360-name">${doc.customer_name} ${doc.is_starred ? '★' : ''}</div>
						<div class="c360-sub">${doc.territory || __("未设置区域")} · ${doc.customer_group || __("未分组")}</div>
					</div>
					<div class="c360-tags">
						${doc.is_public_pool ? `<span class="tag tag-warn">${__('公海')}</span>` : ''}
						${doc.is_starred ? `<span class="tag tag-hot">${__('热点')}</span>` : ''}
						<span class="tag">${__("负责人：")}${owner}</span>
					</div>
				</div>
				<div class="c360-contact">
					<span>📧 ${doc.email_id || '—'}</span>
					<span>📱 ${doc.phone || '—'}</span>
				</div>
				<div class="c360-stats">
					<div class="stat"><div class="stat-num">${doc.follows.length}</div><div class="stat-label">${__("跟进")}</div></div>
					<div class="stat"><div class="stat-num">${doc.opps.length}</div><div class="stat-label">${__("商机")}</div></div>
					<div class="stat"><div class="stat-num">${doc.quots.length}</div><div class="stat-label">${__("报价")}</div></div>
					<div class="stat"><div class="stat-num">${doc.orders.length}</div><div class="stat-label">${__("订单")}</div></div>
					<div class="stat"><div class="stat-num">${so_total ? frappe.format(so_total, { fieldtype: 'Currency', currency: doc.orders[0] && doc.orders[0].currency }) : '—'}</div><div class="stat-label">${__("订单额")}</div></div>
					<div class="stat"><div class="stat-num">${doc.mails.length}</div><div class="stat-label">${__("邮件")}</div></div>
				</div>
			</div>

			<div class="c360-grid">
				<div class="card c360-follow">
					<div class="c360-sec-title">${__("跟进时间线")}</div>
					${doc.follows.length ? doc.follows.map(f => `
						<div class="c360-tl-item">
							<div class="c360-tl-dot"></div>
							<div class="c360-tl-body">
								<div class="c360-tl-head"><span class="tag">${f.follow_type || __('跟进')}</span><span class="c360-tl-date">${(f.follow_date || '').toString().slice(0, 10)}</span>
								${f.next_follow_date ? `<span class="c360-tl-next">${__("下次：")}${f.next_follow_date}</span>` : ''}</div>
								<div class="c360-tl-content">${f.content || ''}</div>
							</div>
						</div>`).join('') : `<div class="c360-empty">${__('暂无跟进记录')}</div>`}
				</div>

				<div class="card">
					<div class="c360-sec-title">${__("商机")}</div>
					${this.listRows(doc.opps, o => [o.title || o.name, o.status, frappe.format(o.opportunity_amount, { fieldtype: 'Currency', currency: o.currency || undefined })], o => o.review_status ? `<span class="tag">${o.review_status}</span>` : '') || `<div class="c360-empty">${__('暂无商机')}</div>`}
				</div>
				<div class="card">
					<div class="c360-sec-title">${__("报价")}</div>
					${this.listRows(doc.quots, q => [q.name, (q.transaction_date || '').toString().slice(0, 10), frappe.format(q.grand_total, { fieldtype: 'Currency', currency: q.currency || undefined })]) || `<div class="c360-empty">${__('暂无报价')}</div>`}
				</div>
				<div class="card">
					<div class="c360-sec-title">${__("销售订单")}</div>
					${this.listRows(doc.orders, o => [o.name, (o.transaction_date || '').toString().slice(0, 10), frappe.format(o.grand_total, { fieldtype: 'Currency', currency: o.currency || undefined })]) || `<div class="c360-empty">${__('暂无订单')}</div>`}
				</div>
				<div class="card">
					<div class="c360-sec-title">${__("相关邮件")}</div>
					${this.listRows(doc.mails, m => [m.subject, m.folder, (m.sent_at || '').toString().slice(0, 16).replace('T', ' ')]) || `<div class="c360-empty">${__('暂无相关邮件')}</div>`}
				</div>
			</div>`;
	},

	listRows(rows, cols, extra) {
		if (!rows.length) return '';
		return `<table class="c360-table"><tbody>${rows.map(r =>
			`<tr>${cols(r).map(c => `<td>${c == null ? '—' : c}</td>`).join('')}${extra ? `<td>${extra(r)}</td>` : ''}</tr>`
		).join('')}</tbody></table>`;
	},

	openForm() {
		frappe.set_route('desk', 'customer', this.customer);
	},

	openShare() {
		const d = new frappe.ui.Dialog({
			title: __("共享客户：{0}", [this.customer]),
			fields: [
				{ fieldname: 'user', fieldtype: 'Link', label: __('共享给'), options: 'User', reqd: 1 },
				{ fieldname: 'read', fieldtype: 'Check', label: __('只读'), default: 1 },
				{ fieldname: 'write', fieldtype: 'Check', label: __('共同负责（可编辑）') },
			],
			primary_action: (v) => {
				frappe.call({
					method: 'general_erp.general_erp.crm_utils.share_customer',
					args: { name: this.customer, user: v.user, read: v.read ? 1 : 0, write: v.write ? 1 : 0 },
				}).then(() => { frappe.show_alert({ indicator: 'green', message: __('已共享') }); d.hide(); });
			},
		});
		d.show();
	},

	openMerge() {
		const d = new frappe.ui.Dialog({
			title: __("合并客户到「{0}」", [this.customer]),
			fields: [
				{ fieldname: 'html', fieldtype: 'HTML' },
			],
			primary_action_label: __('合并'),
			primary_action: (v) => {
				const drops = [...d.wrapper.querySelectorAll('input[type=checkbox]:checked')].map(i => i.value);
				if (!drops.length) return frappe.msgprint(__('请至少选择一个待合并客户'));
				frappe.confirm(
					__("将 {0} 个客户并入「{1}」，源客户将停用并标记。确定？", [drops.length, this.customer]),
					() => frappe.call({
						method: 'general_erp.general_erp.crm_utils.merge_customers',
						args: { keep: this.customer, drop: drops.join(',') },
					}).then(() => { frappe.msgprint(__('合并完成')); d.hide(); this.render(); }),
				);
			},
		});
		d.show();
		frappe.db.get_list('Customer', { filters: { name: ['!=', this.customer], merged_into: ['', null], disabled: 0 }, fields: ['name', 'customer_name', 'email_id'], limit: 50 })
			.then(list => {
				d.get_field('html').wrap.innerHTML = list.length
					? `<div class="c360-merge-list">${list.map(c => `<label><input type="checkbox" value="${c.name}"> ${c.customer_name} <span class="c360-sub">${c.email_id || ''}</span></label>`).join('')}</div>`
					: __('没有可合并的客户');
			});
	},

	openHandover() {
		const d = new frappe.ui.Dialog({
			title: __('移交客户'),
			fields: [
				{ fieldname: 'to_user', fieldtype: 'Link', label: __('移交至'), options: 'User', reqd: 1 },
				{ fieldname: 'remark', fieldtype: 'Small Text', label: __('原因/备注') },
			],
			primary_action: (v) => frappe.call({
				method: 'general_erp.general_erp.doctype.customer_follow_up.customer_follow_up.handover_customer',
				args: { name: this.customer, to_user: v.to_user, remark: v.remark },
			}).then(() => { frappe.msgprint(__('移交成功')); d.hide(); this.render(); }),
		});
		d.show();
	},
};

function make(wrapper) {
	wrapper.innerHTML = `
		<div class="c360-wrap">
			<div class="c360-head">
				<div>
					<div class="c360-title">${__('客户 360')}</div>
					<div class="c360-subtitle">${__('客户详情聚合：跟进时间线 · 商机 · 报价 · 订单 · 邮件')}</div>
				</div>
				<div class="c360-picker">
					<input class="c360-input" list="c360-custs" placeholder="${__('选择客户…')}" />
					<datalist id="c360-custs"></datalist>
					<button class="btn btn-primary btn-sm c360-go">${__('查看')}</button>
				</div>
				<div class="c360-actions" style="visibility:hidden">
					<button class="btn btn-sm c360-form">${__('打开表单')}</button>
					<button class="btn btn-sm c360-share">${__('共享')}</button>
					<button class="btn btn-sm c360-merge">${__('合并')}</button>
					<button class="btn btn-sm c360-handover">${__('移交')}</button>
				</div>
			</div>
			<div class="c360-main"><div class="c360-loading">${__('请选择一个客户查看 360 视图')}</div></div>
		</div>`;

	frappe.db.get_list('Customer', { fields: ['name', 'customer_name'], limit: 500 }).then(list => {
		wrapper.querySelector('#c360-custs').innerHTML = list.map(c => `<option value="${c.name}">${c.customer_name}</option>`).join('');
	});

	const input = wrapper.querySelector('.c360-input');
	wrapper.querySelector('.c360-go').addEventListener('click', () => {
		if (!input.value.trim()) return;
		const opt = [...wrapper.querySelector('#c360-custs').options].find(o => o.value === input.value.trim() || o.textContent === input.value.trim());
		C360.customer = opt ? opt.value : input.value.trim();
		wrapper.querySelector('.c360-actions').style.visibility = 'visible';
		location.search = `?customer=${encodeURIComponent(C360.customer)}`;
		C360.render();
	});
	input.addEventListener('keydown', (e) => { if (e.key === 'Enter') wrapper.querySelector('.c360-go').click(); });
	wrapper.querySelector('.c360-form').addEventListener('click', () => C360.openForm());
	wrapper.querySelector('.c360-share').addEventListener('click', () => C360.openShare());
	wrapper.querySelector('.c360-merge').addEventListener('click', () => C360.openMerge());
	wrapper.querySelector('.c360-handover').addEventListener('click', () => C360.openHandover());

	C360.load();
}

frappe.pages['customer-360'].on_page_load = function (wrapper) {
	make(wrapper);
};
