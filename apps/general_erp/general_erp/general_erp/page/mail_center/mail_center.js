/* 邮件中心：内部协作邮件（文件夹 + 状态流转），数据走 Mail 单据的白名单接口 */

const MC = {
	all: [],
	tab: '全部',

	tabs: [
		{ key: '全部', folder: null, status: null },
		{ key: '待处理', folder: null, status: '待处理' },
		{ key: '待审批', folder: null, status: '待审批' },
		{ key: '收件箱', folder: '收件箱', status: null },
		{ key: '已发送', folder: '已发送', status: null },
		{ key: '草稿箱', folder: '草稿箱', status: null },
		{ key: '已删除', folder: '已删除', status: null },
	],

	statusBadge(s) {
		const cls = { '待处理': 'st-warn', '待审批': 'st-info', '已处理': 'st-ok', '已删除': 'st-muted' }[s] || 'st-muted';
		return `<span class="mc-badge ${cls}">${__(s)}</span>`;
	},

	actions(m) {
		const btn = (label, act) => `<span class="mc-act" data-act="${act}" data-name="${m.name}">${label}</span>`;
		const out = [];
		if (m.folder === '收件箱' || m.folder === '草稿箱') {
			if (m.status === '待处理') out.push(btn(__('待审批'), 'pending'));
			out.push(btn(__('删除'), 'trash'));
		} else if (m.folder === '已发送') {
			out.push(btn(__('删除'), 'trash'));
		} else if (m.folder === '已删除') {
			out.push(btn(__('恢复'), 'restore'));
		}
		if (m.status === '待处理' && m.folder === '收件箱') out.push(btn(__('已处理'), 'done'));
		if (m.status === '待审批') out.push(btn(__('已处理'), 'done'));
		return out.join('');
	},

	row(m) {
		const related = m.related_doctype ? `<span class="mc-rel">${m.related_doctype}${m.related_name ? ' · ' + m.related_name : ''}</span>` : '';
		const time = (m.sent_at || m.creation || '').toString().slice(0, 16).replace('T', ' ');
		const who = m.folder === '已发送'
			? `${m.sender_name} → ${m.recipient_name || '-'}`
			: `${m.sender_name || '-'} → ${m.recipient_name || frappe.session.user}`;
		return `
			<tr>
				<td class="mc-subject"><div>${m.subject} ${related}</div></td>
				<td>${who}</td>
				<td><span class="mc-badge st-folder">${__(m.folder)}</span> ${this.statusBadge(m.status)}</td>
				<td class="mc-time">${time}</td>
				<td class="mc-actions">${this.actions(m)}</td>
			</tr>`;
	},

	setTab(key) {
		this.tab = key;
		document.querySelectorAll('.mc-tab').forEach((t) => t.classList.toggle('is-active', t.dataset.tab === key));
	},

	match(m) {
		const t = this.tabs.find((x) => x.key === this.tab);
		if (!t.folder && !t.status) return true;
		if (t.folder && m.folder !== t.folder) return false;
		if (t.status && m.status !== t.status) return false;
		return true;
	},

	async renderList() {
		const body = document.querySelector('.mc-table tbody');
		const rows = this.all.filter((m) => this.match(m));
		body.innerHTML = rows.length
			? rows.map((m) => this.row(m)).join('')
			: `<tr><td colspan="5" class="mc-empty">${__("暂无邮件")}</td></tr>`;
		this.tabs.forEach((t) => {
			const count = this.all.filter((m) => {
				if (!t.folder && !t.status) return true;
				if (t.folder && m.folder !== t.folder) return false;
				if (t.status && m.status !== t.status) return false;
				return true;
			}).length;
			const el = document.querySelector(`.mc-tab[data-tab="${t.key}"] .mc-count`);
			if (el) el.textContent = count;
		});
	},

	async refresh() {
		this.all = await frappe.xcall('general_erp.general_erp.doctype.mail.mail.get_mails');
		await this.renderList();
	},

	bindEvents(wrapper) {
		wrapper.querySelectorAll('.mc-tab').forEach((el) => {
			el.addEventListener('click', () => {
				this.tab = el.dataset.tab;
				wrapper.querySelectorAll('.mc-tab').forEach((t) => t.classList.toggle('is-active', t === el));
				this.renderList();
			});
		});
		wrapper.querySelector('.mc-table').addEventListener('click', (e) => {
			const btn = e.target.closest('.mc-act');
			if (!btn) return;
			const { act, name } = btn.dataset;
			const m = this.all.find((x) => x.name === name);
			if (act === 'done') this.update(name, { status: '已处理' });
			else if (act === 'pending') this.update(name, { status: '待审批' });
			else if (act === 'trash') this.update(name, { folder: '已删除', status: '已处理' });
			else if (act === 'restore') {
				const folder = (m && m.restore_folder) || (m && m.sender === frappe.session.user ? '已发送' : '收件箱');
				const status = (m && m.restore_status) || (folder === '收件箱' ? '待处理' : '已处理');
				this.update(name, { folder, status });
			}
		});
	},

	update(name, fields) {
		return frappe
			.call({
				method: 'general_erp.general_erp.doctype.mail.mail.update_mail',
				args: { name, ...fields },
			})
			.then(() => this.refresh());
	},

	openCompose() {
		const d = new frappe.ui.Dialog({
			title: __('新邮件'),
			fields: [
				{ fieldname: 'recipient', label: __('收件人'), fieldtype: 'Link', options: 'User', reqd: 1 },
				{ fieldname: 'subject', label: __('主题'), fieldtype: 'Data', reqd: 1 },
				{ fieldname: 'body', label: __('正文'), fieldtype: 'Text Editor' },
			],
			primary_action: (values) => {
				frappe
					.call({
						method: 'general_erp.general_erp.doctype.mail.mail.create_mail',
						args: { ...values, folder: '已发送', sender: frappe.session.user, status: '已处理' },
					})
					.then(() => {
						d.hide();
						this.tab = '已发送';
						this.refresh();
					});
			},
			primary_action_label: __('发送'),
			secondary_action: () => {
				const values = d.get_values();
				if (!values) return;
				frappe
					.call({
						method: 'general_erp.general_erp.doctype.mail.mail.create_mail',
						args: { ...values, folder: '草稿箱', sender: frappe.session.user, status: '已处理' },
					})
					.then(() => {
						d.hide();
						this.tab = '草稿箱';
						this.refresh();
					});
			},
			secondary_action_label: __('存草稿'),
		});
		d.show();
	},
};

function make(wrapper) {
	const wrap = document.createElement('div');
	wrap.className = 'mail-center-wrap';

	const tabsHtml = MC.tabs.map((t, i) =>
		`<span class="mc-tab${i === 0 ? ' is-active' : ''}" data-tab="${t.key}">${__(t.key)}<span class="mc-count">0</span></span>`
	).join('');

	wrap.innerHTML = `
		<div class="mail-center-head">
			<div>
				<div class="mail-center-title">${__("邮件中心")}</div>
				<div class="mail-center-sub">${__("内部协作邮件 · 待处理 / 收件箱 / 已发送 / 草稿箱 / 待审批 / 已删除")}</div>
			</div>
			<button class="btn btn-primary btn-sm mc-compose">${__("新邮件")}</button>
		</div>
		<div class="mc-tabs">${tabsHtml}</div>
		<div class="mc-card">
			<table class="mc-table">
				<thead>
					<tr><th>${__("主题")}</th><th>${__("发件人 / 收件人")}</th><th>${__("文件夹 / 状态")}</th><th>${__("时间")}</th><th>${__("操作")}</th></tr>
				</thead>
				<tbody></tbody>
			</table>
		</div>`;

	wrapper.append(wrap);
	MC.bindEvents(wrapper);
	wrap.querySelector('.mc-compose').addEventListener('click', () => MC.openCompose());
	MC.refresh();
}

/* 页面注册：frappe.views.Page 构造时 eval 本脚本，随后触发 wrapper.on_page_load(wrapper） */
frappe.pages['mail-center'].on_page_load = function (wrapper) {
	make(wrapper);
};
