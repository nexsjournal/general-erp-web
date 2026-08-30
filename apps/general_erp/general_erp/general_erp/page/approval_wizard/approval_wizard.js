// T-approval-wizard: 审批设置向导（流程清单 + 三问式新建/编辑 + 待我审批）
const APPROVAL_API = 'general_erp.api_approval_wizard';

function esc(s) {
	return String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}

function awCall(method, args, onOk, onErr) {
	frappe.call({
		method: APPROVAL_API + '.' + method,
		args: args || {},
		freeze: true,
		callback: (res) => {
			if (res.exc) {
				const raw = (res._server_messages && res._server_messages[0]) || res.exc || '操作失败';
				const msg = String(raw).replace(/<[^>]+>/g, '').replace(/&quot;/g, '"');
				(onErr || frappe.msgprint)({ title: '提示', message: msg, indicator: 'red' });
				return;
			}
			onOk(res.message);
		},
	});
}

function awRoleName(r) {
	const sel = document.getElementById('aw-start');
	if (sel) {
		const o = [...sel.options].find(x => x.value === r);
		if (o) return o.text;
	}
	return r;
}

// ---------------- 流程清单 ----------------
function awLoadList(root) {
	const box = root.querySelector('#aw-list-view');
	box.innerHTML = '<div style="padding:20px;color:#999">加载中…</div>';
	awCall('list_workflows', {}, (rows) => {
		if (!rows.length) {
			box.innerHTML = '<div style="padding:20px;color:#999">暂无审批流程，点右上角「新建审批流程」</div>';
			return;
		}
		let html = '<table class="aw-table"><thead><tr><th>流程名称</th><th>适用单据</th><th>发起角色</th><th>审批链</th><th>免批条件</th><th>状态</th><th>操作</th></tr></thead><tbody>';
		rows.forEach(w => {
			const chain = (w.chain || []).map(c => c.state + '·' + c.role_labels.join('/')).join(' → ') || '—';
			const cond = w.min_approval_amount ? esc(w.min_approval_amount) + ' 元以下免批' : '—';
			html += '<tr>'
				+ '<td><b>' + esc(w.name) + '</b></td>'
				+ '<td>' + esc(w.dt_label) + '</td>'
				+ '<td>' + esc((w.start_role_labels || []).join(' / ') || '—') + '</td>'
				+ '<td>' + esc(chain) + '</td>'
				+ '<td>' + cond + '</td>'
				+ '<td>' + (w.is_active ? '<span class="aw-tag on">启用中</span>' : '<span class="aw-tag off">已停用</span>') + '</td>'
				+ '<td>'
				+ '<button class="btn btn-xs aw-edit" data-wf="' + esc(w.name) + '">编辑</button> '
				+ '<button class="btn btn-xs aw-toggle" data-wf="' + esc(w.name) + '" data-on="' + (w.is_active ? 0 : 1) + '">' + (w.is_active ? '停用' : '启用') + '</button>'
				+ '</td></tr>';
		});
		html += '</tbody></table>';
		box.innerHTML = html;
		box.querySelectorAll('.aw-edit').forEach(b => b.addEventListener('click', () => awOpenWizard(root, b.dataset.wf)));
		box.querySelectorAll('.aw-toggle').forEach(b => b.addEventListener('click', () => {
			awCall('set_workflow_active', { wf_name: b.dataset.wf, is_active: Number(b.dataset.on) }, () => awLoadList(root));
		}));
	});
}

// ---------------- 待我审批 ----------------
function awLoadMine(root) {
	const box = root.querySelector('#aw-mine-view');
	box.innerHTML = '<div style="padding:20px;color:#999">加载中…</div>';
	awCall('get_my_approvals', {}, (rows) => {
		const countEl = root.querySelector('#aw-mine-count');
		if (countEl) countEl.textContent = rows.length ? String(rows.length) : '';
		if (!rows.length) {
			box.innerHTML = '<div style="padding:20px;color:#999">🎉 没有待你审批的单据</div>';
			return;
		}
		let html = '<table class="aw-table"><thead><tr><th>单据</th><th>类型</th><th>状态</th><th>金额</th><th>等待时长</th><th>操作</th></tr></thead><tbody>';
		rows.forEach(r => {
			const age = r.age_hours >= 24 ? (Math.floor(r.age_hours / 24) + ' 天 ' + (r.age_hours % 24) + ' 小时') : (r.age_hours + ' 小时');
			html += '<tr>'
				+ '<td><a href="' + esc(r.url) + '" target="_blank"><b>' + esc(r.name) + '</b></a></td>'
				+ '<td>' + esc(r.doctype_label) + '</td>'
				+ '<td>' + esc(r.state) + '</td>'
				+ '<td>' + (r.amount != null ? Number(r.amount).toLocaleString('zh-CN') + ' 元' : '—') + '</td>'
				+ '<td class="' + (r.urgent ? 'aw-urgent' : '') + '">' + age + (r.urgent ? ' ⚠' : '') + '</td>'
				+ '<td><a class="btn btn-xs btn-primary" href="' + esc(r.url) + '" target="_blank">去审批</a></td>'
				+ '</tr>';
		});
		box.innerHTML = html + '</tbody></table>';
	});
}

// ---------------- 向导 ----------------
function awAddLevelRow(box, roles) {
	const startSel = document.getElementById('aw-start');
	const roleHtml = [...startSel.options].map(o => '<option value="' + esc(o.value) + '">' + esc(o.text) + '</option>').join('');
	const row = document.createElement('div');
	row.className = 'aw-level-row';
	row.innerHTML = '<span class="aw-level-num">' + (box.children.length + 1) + '</span>'
		+ '<select class="aw-input aw-level-roles" multiple size="3">' + roleHtml + '</select>'
		+ '<button class="btn btn-xs aw-rm-level">删除</button>';
	(roles || []).forEach(r => [...row.querySelectorAll('option')].forEach(o => { if (o.value === r) o.selected = true; }));
	row.querySelector('.aw-rm-level').addEventListener('click', () => { row.remove(); awRenumber(); });
	box.appendChild(row);
	awRenumber();
}

function awRenumber() {
	document.querySelectorAll('#aw-levels .aw-level-row').forEach((r, i) => {
		r.querySelector('.aw-level-num').textContent = String(i + 1);
	});
}

function awCollect(root) {
	const doctype = document.getElementById('aw-doctype').value;
	const amountField = (document.querySelector('#aw-doctype option:checked') || {}).dataset ? document.querySelector('#aw-doctype option:checked').dataset.af || '' : '';
	const start = [...document.getElementById('aw-start').selectedOptions].map(o => o.value);
	const levels = [...document.querySelectorAll('#aw-levels .aw-level-row')].map(r => ({
		roles: [...r.querySelectorAll('option:checked')].map(o => o.value),
	}));
	const minOn = document.getElementById('aw-min-on').checked && !!amountField;
	const minAmount = document.getElementById('aw-min').value || '';
	const timeoutOn = document.getElementById('aw-timeout-on').checked;
	const timeoutH = document.getElementById('aw-timeout').value || '24';
	return { doctype, amountField, start, levels, minOn, minAmount, timeoutOn, timeoutH };
}

function awUpdatePreview() {
	const c = awCollect(document.querySelector('.approval-wiz-wrap'));
	const pv = document.getElementById('aw-preview');
	if (!pv) return;
	const startLabels = c.start.map(awRoleName).join(' / ') || '—';
	const chainParts = c.levels.map((lv, i) => '第' + (i + 1) + '级 ' + (lv.roles.map(awRoleName).join('/') || '?'));
	const cond = (c.minOn && c.minAmount)
		? '金额 ≥ ' + c.minAmount + ' 元走审批，低于 ' + c.minAmount + ' 元发起人可选「免批通过」'
		: '所有单据都走审批（未设免批）';
	pv.innerHTML = '<b>流程预览</b><div class="aw-fp-line">'
		+ '<span class="aw-fp-node">' + esc(startLabels) + '<small>发起</small></span><span>→</span>'
		+ chainParts.map(p => '<span class="aw-fp-node">' + esc(p) + '</span><span>→</span>').join('')
		+ '<span class="aw-fp-node ok">完成</span></div>'
		+ '<div class="aw-hint">' + esc(cond) + (c.timeoutOn ? ' · 超 ' + c.timeoutH + ' 小时催办审批人' : '') + '</div>';
}

function awFillWizard(cur) {
	const sel = document.getElementById('aw-doctype');
	[...sel.options].forEach(o => { if (o.value === cur.document_type) o.selected = true; });
	const start = document.getElementById('aw-start');
	(cur.start_roles || []).forEach(r => [...start.options].forEach(o => { if (o.value === r) o.selected = true; }));
	const lvBox = document.getElementById('aw-levels');
	lvBox.innerHTML = '';
	(cur.chain || []).forEach(c => awAddLevelRow(lvBox, c.roles || []));
	if (!lvBox.children.length) awAddLevelRow(lvBox, []);
	const minOn = document.getElementById('aw-min-on');
	minOn.checked = !!cur.min_approval_amount;
	if (cur.min_approval_amount) document.getElementById('aw-min').value = cur.min_approval_amount;
	const toOn = document.getElementById('aw-timeout-on');
	toOn.checked = !!cur.approval_timeout_hours;
	if (cur.approval_timeout_hours) document.getElementById('aw-timeout').value = cur.approval_timeout_hours;
	minOn.dispatchEvent(new Event('change'));
}

function awOpenWizard(root, wfName) {
	root.querySelector('#aw-list-view').style.display = 'none';
	root.querySelector('#aw-mine-view').style.display = 'none';
	const box = root.querySelector('#aw-wizard-view');
	box.style.display = '';
	box.innerHTML = '<div style="padding:20px;color:#999">加载中…</div>';
	awCall('get_options', {}, (opts) => {
		const draw = (cur) => {
			box.innerHTML = ''
				+ '<div class="aw-wiz-head"><button class="btn aw-back">← 返回</button><h3>' + (wfName ? '编辑审批流程：' + esc(wfName) : '新建审批流程') + '</h3></div>'
				+ '<div class="aw-steps"><span class="on">① 选单据</span><span>② 定审批链</span><span>③ 智能选项</span></div>'
				+ '<div class="aw-field"><label>适用单据</label><select id="aw-doctype" class="aw-input">'
				+ opts.doc_types.map(d => '<option value="' + esc(d.value) + '" data-af="' + esc(d.amount_field || '') + '">' + esc(d.label) + '</option>').join('')
				+ '</select></div>'
				+ '<div class="aw-field"><label>谁发起（可多选，按住 Ctrl/⌘ 点选多个）</label>'
				+ '<select id="aw-start" class="aw-input" multiple size="6">' + opts.roles.map(r => '<option value="' + esc(r.value) + '">' + esc(r.label) + '</option>').join('') + '</select>'
				+ '<div class="aw-hint">这些人新建单据并点「提交审批」。</div></div>'
				+ '<div class="aw-field"><label>审批链（每级选审批角色，最多 3 级；驳回退回发起人）</label>'
				+ '<div id="aw-levels"></div><button class="btn aw-add-level">＋ 添加一级审批</button></div>'
				+ '<div class="aw-field"><label>智能选项（都有合理默认值，直接保存也行）</label>'
				+ '<div class="aw-switch-row"><label class="aw-switch"><input type="checkbox" id="aw-min-on"><span></span></label><div>'
				+ '<b>小额免批</b>：金额低于阈值时，发起人可选「免批通过」直接生效'
				+ '<div class="aw-hint" id="aw-min-line">金额低于 <input class="aw-input aw-amount" id="aw-min" type="number" value="5000"> 元免批（留空 = 不限制）</div>'
				+ '<div class="aw-hint" id="aw-min-nosupport" style="display:none">该单据没有金额字段，暂不支持小额免批</div></div></div>'
				+ '<div class="aw-switch-row"><label class="aw-switch"><input type="checkbox" id="aw-timeout-on" checked><span></span></label><div>'
				+ '<b>超时催办</b>：超过 <input class="aw-input aw-amount" id="aw-timeout" type="number" value="24"> 小时没审批，自动提醒审批人（系统通知铃铛）</div></div>'
				+ '</div>'
				+ '<div class="aw-preview" id="aw-preview"></div>'
				+ '<div class="aw-actions"><button class="btn aw-back">取消</button><button class="btn btn-primary aw-save">保存并启用</button></div>';
			if (cur) awFillWizard(cur);
			// 事件绑定
			box.querySelectorAll('.aw-back').forEach(b => b.addEventListener('click', () => {
				box.style.display = 'none';
				root.querySelector('#aw-list-view').style.display = '';
				awLoadList(root);
			}));
			box.querySelector('.aw-add-level').addEventListener('click', () => {
				const lb = document.getElementById('aw-levels');
				if (lb.children.length >= 3) { frappe.msgprint('最多支持 3 级审批'); return; }
				awAddLevelRow(lb, []);
				awUpdatePreview();
			});
			document.getElementById('aw-doctype').addEventListener('change', () => {
				const af = (document.querySelector('#aw-doctype option:checked') || {}).dataset ? document.querySelector('#aw-doctype option:checked').dataset.af || '' : '';
				document.getElementById('aw-min-line').style.display = af ? '' : 'none';
				document.getElementById('aw-min-nosupport').style.display = af ? 'none' : '';
				awUpdatePreview();
			});
			document.getElementById('aw-min-on').addEventListener('change', function() {
				document.getElementById('aw-min-line').style.visibility = this.checked ? 'visible' : 'hidden';
				awUpdatePreview();
			});
			document.getElementById('aw-min').addEventListener('input', awUpdatePreview);
			document.getElementById('aw-timeout').addEventListener('input', awUpdatePreview);
			document.getElementById('aw-start').addEventListener('change', awUpdatePreview);
			box.querySelector('.aw-save').addEventListener('click', function() {
				const c = awCollect(root);
				if (!c.start.length) { frappe.msgprint('请至少选一个发起角色'); return; }
				if (!c.levels.length) { frappe.msgprint('请至少添加一级审批'); return; }
				if (c.levels.some(lv => !lv.roles.length)) { frappe.msgprint('每一级审批都要选至少一个角色'); return; }
				this.disabled = true;
				awCall('save_workflow', {
					wf_name: '',
					document_type: c.doctype,
					start_roles: JSON.stringify(c.start),
					levels: JSON.stringify(c.levels),
					min_approval_on: c.minOn ? 1 : 0,
					min_approval_amount: c.minOn ? (c.minAmount || 0) : 0,
					timeout_hours: c.timeoutOn ? c.timeoutH : 0,
					is_active: 1,
				}, (res) => {
					this.disabled = false;
					frappe.show_alert({ message: '流程「' + (res && res.name) + '」已保存并启用，全员刷新后生效', indicator: 'green' });
					box.style.display = 'none';
					root.querySelector('#aw-list-view').style.display = '';
					awLoadList(root);
				});
			});
			awUpdatePreview();
		};
		if (wfName) {
			awCall('get_workflow_detail', { wf_name: wfName }, draw);
		} else {
			draw(null);
		}
	});
}

// ---------------- 页面主体 ----------------
const AW_APPROVAL_PAGE = function(wrapper) {
	const el = document.createElement('div');
	el.className = 'approval-wiz-wrap';
	el.innerHTML = ''
		+ '<div class="aw-tabs">'
		+ '<div class="aw-tab active" data-tab="list">审批流程</div>'
		+ '<div class="aw-tab" data-tab="mine">待我审批 <span class="aw-badge" id="aw-mine-count"></span></div>'
		+ '<button class="btn btn-primary aw-new-btn" id="aw-new">＋ 新建审批流程</button>'
		+ '</div>'
		+ '<div id="aw-list-view"></div>'
		+ '<div id="aw-mine-view" style="display:none"></div>'
		+ '<div id="aw-wizard-view" style="display:none"></div>';
	wrapper.append(el);
	el.querySelectorAll('.aw-tab').forEach(t => t.addEventListener('click', () => {
		el.querySelectorAll('.aw-tab').forEach(x => x.classList.toggle('active', x === t));
		el.querySelector('#aw-list-view').style.display = t.dataset.tab === 'list' ? '' : 'none';
		el.querySelector('#aw-mine-view').style.display = t.dataset.tab === 'mine' ? '' : 'none';
		el.querySelector('#aw-wizard-view').style.display = 'none';
	}));
	el.querySelector('#aw-new').addEventListener('click', () => awOpenWizard(el, null));
	awLoadList(el);
	awLoadMine(el);
};

frappe.pages['approval-wizard'] = new frappe.ui.Page({
	onload() {
		const css = ''
			+ '.approval-wiz-wrap{padding:16px 24px;font-size:14px}'
			+ '.aw-tabs{display:flex;align-items:center;gap:16px;border-bottom:1px solid #e5e7eb;margin-bottom:16px;padding-bottom:10px}'
			+ '.aw-tab{cursor:pointer;padding:6px 12px;border-radius:8px;color:#6b7280}'
			+ '.aw-tab.active{background:#dbeafe;color:#1d4ed8;font-weight:600}'
			+ '.aw-new-btn{margin-left:auto}'
			+ '.aw-badge{background:#dc2626;color:#fff;border-radius:99px;padding:0 8px;font-size:12px}'
			+ '.aw-table{width:100%;border-collapse:collapse;background:#fff;border-radius:10px;overflow:hidden}'
			+ '.aw-table th{text-align:left;font-weight:500;color:#6b7280;font-size:13px;padding:10px 12px;border-bottom:1px solid #e5e7eb;background:#f9fafb}'
			+ '.aw-table td{padding:12px;border-bottom:1px solid #f3f4f6}'
			+ '.aw-tag{display:inline-block;padding:2px 10px;border-radius:99px;font-size:12px}'
			+ '.aw-tag.on{background:#dcfce7;color:#166534}'
			+ '.aw-tag.off{background:#f3f4f6;color:#6b7280}'
			+ '.aw-urgent{color:#dc2626;font-weight:600}'
			+ '.aw-field{margin-bottom:18px}'
			+ '.aw-field label{display:block;font-weight:500;margin-bottom:6px}'
			+ '.aw-input{width:100%;max-width:420px;padding:8px 12px;border:1px solid #d1d5db;border-radius:8px;font-size:14px}'
			+ 'select.aw-input[multiple]{max-width:520px}'
			+ '.aw-hint{color:#9ca3af;font-size:12px;margin-top:4px}'
			+ '.aw-amount{width:110px;padding:4px 8px}'
			+ '.aw-level-row{display:flex;align-items:center;gap:12px;padding:10px;border:1px solid #e5e7eb;border-radius:10px;margin-bottom:10px}'
			+ '.aw-level-row select{max-width:420px}'
			+ '.aw-level-num{width:28px;height:28px;border-radius:50%;background:#2563eb;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:600;flex-shrink:0}'
			+ '.aw-switch-row{display:flex;align-items:flex-start;gap:10px;padding:12px;background:#f9fafb;border-radius:10px;margin-bottom:10px}'
			+ '.aw-switch{position:relative;width:40px;height:22px;flex-shrink:0;margin-top:2px}'
			+ '.aw-switch input{opacity:0;width:0;height:0}'
			+ '.aw-switch span{position:absolute;inset:0;background:#d1d5db;border-radius:99px;cursor:pointer;transition:.2s}'
			+ '.aw-switch span:before{content:"";position:absolute;width:18px;height:18px;left:2px;top:2px;background:#fff;border-radius:50%;transition:.2s}'
			+ '.aw-switch input:checked+span{background:#2563eb}'
			+ '.aw-switch input:checked+span:before{transform:translateX(18px)}'
			+ '.aw-preview{background:#f9fafb;border:1px dashed #d1d5db;border-radius:10px;padding:14px}'
			+ '.aw-fp-line{display:flex;align-items:center;flex-wrap:wrap;gap:6px;margin-top:8px}'
			+ '.aw-fp-node{background:#fff;border:1px solid #e5e7eb;border-radius:8px;padding:6px 12px;font-size:13px}'
			+ '.aw-fp-node small{display:block;color:#6b7280}'
			+ '.aw-fp-node.ok{background:#dcfce7;border-color:#bbf7d0}'
			+ '.aw-actions{display:flex;justify-content:flex-end;gap:10px;margin-top:20px}'
			+ '.aw-wiz-head{display:flex;align-items:center;gap:14px;margin-bottom:10px}'
			+ '.aw-steps{display:flex;gap:8px;margin-bottom:16px}'
			+ '.aw-steps span{padding:6px 12px;border-radius:8px;background:#f3f4f6;color:#9ca3af;font-size:13px}'
			+ '.aw-steps span.on{background:#dbeafe;color:#1d4ed8;font-weight:600}';
		const style = document.createElement('style');
		style.textContent = css;
		document.head.appendChild(style);
	},
	onload_post_render() {
		AW_APPROVAL_PAGE(this.inner);
	},
});
