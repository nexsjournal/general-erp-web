/* 业务流程展示页（演示用）：按功能清单梳理核心业务流程，串联现有单据 */

const I = (p) => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${p}</svg>`;

const ICONS = {
	user: I('<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>'),
	users: I('<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>'),
	file: I('<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M9 13h6M9 17h6"/>'),
	clipboard: I('<rect x="8" y="2" width="8" height="4" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="M9 12h6M9 16h6"/>'),
	clipboardcheck: I('<rect x="8" y="2" width="8" height="4" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/>'),
	anchor: I('<circle cx="12" cy="5" r="3"/><path d="M12 22V8"/><path d="M5 12H2a10 10 0 0 0 20 0h-3"/>'),
	filecheck: I('<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="m9.5 14.5 1.5 1.5 3-3"/>'),
	banknote: I('<rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="2.5"/><path d="M6 12h.01M18 12h.01"/>'),
	package: I('<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><path d="M3.3 7 12 12l8.7-5"/><path d="M12 22V12"/>'),
	searchcheck: I('<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/><path d="m8.5 11.5 2 2 3.5-3.5"/>'),
	box: I('<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>'),
	globe: I('<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3a14 14 0 0 1 0 18 14 14 0 0 1 0-18z"/>'),
	hash: I('<path d="M4 9h16M4 15h16M10 3 8 21M16 3l-2 18"/>'),
	sliders: I('<path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3"/><path d="M1 14h6M9 8h6M17 16h6"/>'),
	chart: I('<path d="M3 3v18h18"/><path d="M8 17v-6M13 17V7M18 17v-4"/>'),
	doc: I('<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/>'),
	clock: I('<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/>'),
	checkc: I('<circle cx="12" cy="12" r="9"/><path d="m8.5 12 2.5 2.5 5-5"/>'),
	x: I('<circle cx="12" cy="12" r="9"/><path d="m9 9 6 6M15 9l-6 6"/>'),
	arrow: I('<path d="M5 12h14"/><path d="m13 6 6 6-6 6"/>'),
	downarrow: I('<path d="M12 5v14"/><path d="m6 13 6 6 6-6"/>'),
	go: I('<path d="M7 17 17 7"/><path d="M8 7h9v9"/>'),
	target: I('<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>'),
	archive: I('<rect x="2" y="3" width="20" height="5" rx="1"/><path d="M4 8v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8"/><path d="M10 12h4"/>'),
	factory: I('<circle cx="12" cy="12" r="3.5"/><path d="M12 2v3.5M12 18.5V22M2 12h3.5M18.5 12H22M4.6 4.6l2.5 2.5M16.9 16.9l2.5 2.5M19.4 4.6l-2.5 2.5M7.1 16.9l-2.5 2.5"/>'),
	megaphone: I('<path d="m3 11 18-6v14L3 13z"/><path d="M11.6 16.8a3 3 0 1 1-5.8-1.6"/>'),
	building: I('<rect x="4" y="3" width="16" height="18" rx="1"/><path d="M9 21v-4h6v4"/><path d="M8 7h.01M12 7h.01M16 7h.01M8 11h.01M12 11h.01M16 11h.01M8 15h.01M16 15h.01"/>'),
	shield: I('<path d="M12 22s8-3.5 8-10V5l-8-3-8 3v7c0 6.5 8 10 8 10z"/>'),
	home: I('<path d="m3 10 9-7 9 7v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/>'),
	mail: I('<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m2 7 10 6 10-6"/>'),
	search: I('<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>'),
	trend: I('<path d="m3 17 6-6 4 4 8-8"/><path d="M14 7h7v7"/>'),
};

/* ---------- 业务数据：功能清单 → 核心业务流程 ---------- */

const LANES = [
	{
		title: '外贸销售主链路',
		desc: '客户获取 → 商机 → 报价 → 订单 → 出运 → 单证 → 收款 → 利润',
		color: 'var(--erp-info)',
		light: 'var(--erp-info-light)',
		steps: [
			{ icon: 'user', label: '客户', sub: '我的客户 · 公海 · 转移/共享', route: ['desk', 'Customer'] },
			{ icon: 'target', label: '商机', sub: '新建商机 · 商机统计', route: ['desk', 'Opportunity'] },
			{ icon: 'file', label: '报价单', sub: '报价管理', route: ['desk', 'Quotation'] },
			{ icon: 'clipboard', label: '销售订单', sub: '外贸订单', route: ['desk', 'Sales Order'] },
			{ icon: 'anchor', label: '出运明细单', sub: '装运港/卸货港 · 贸易术语 · 出运明细', route: ['desk', 'Shipment'], badge: 'General ERP' },
			{ icon: 'filecheck', label: '外贸单证', sub: '单证制作 · 出口报关', route: ['desk', 'Trade Document'], badge: 'General ERP' },
			{ icon: 'banknote', label: '收款', sub: '收款管理 · Payment Entry', route: ['desk', 'Payment Entry'] },
			{ icon: 'trend', label: '订单利润', sub: '订单维度利润分析', route: ['desk', 'query-report', '订单利润'], report: true },
		],
	},
	{
		title: '采购与来料检验',
		desc: '供应商 → 采购 → 入库 → 来料检验',
		color: 'var(--erp-success)',
		light: 'var(--erp-success-light)',
		steps: [
			{ icon: 'users', label: '供应商', sub: '供应商主数据', route: ['desk', 'Supplier'] },
			{ icon: 'clipboardcheck', label: '采购订单', sub: '下达 PO', route: ['desk', 'Purchase Order'] },
			{ icon: 'package', label: '采购入库', sub: 'Purchase Receipt', route: ['desk', 'Purchase Receipt'] },
			{ icon: 'searchcheck', label: '来料验货单', sub: '检验人 · 验货明细 · 结论', route: ['desk', 'Inspection Order'], badge: 'General ERP' },
			{ icon: 'box', label: '物料', sub: '产品库 · HS 编码', route: ['desk', 'Item'] },
		],
	},
	{
		title: '库存管理链路',
		desc: '入库 → 库存余额 → 出库 → 统计 / 预警',
		color: '#0fc6c2',
		light: 'rgba(15, 198, 194, 0.12)',
		steps: [
			{ icon: 'box', label: '入库', sub: 'Stock Entry · 其他入库', route: ['desk', 'Stock Entry'] },
			{ icon: 'archive', label: '库存余额', sub: '库存汇总 · Stock Summary', route: ['desk', 'stock-balance'] },
			{ icon: 'box', label: '出库', sub: 'Delivery Note · 销售出库', route: ['desk', 'Delivery Note'] },
			{ icon: 'chart', label: '库存统计', sub: 'Stock Balance 报表', route: ['desk', 'query-report', 'Stock Balance'], report: true },
			{ icon: 'box', label: '库存预警', sub: '最小/最大 · 再订货点', route: ['desk', 'Item'] },
		],
	},
	{
		title: '生产链路',
	 desc: '生产任务单 → 生产进度',
		color: '#722ed1',
		light: 'rgba(114, 46, 209, 0.12)',
		steps: [
			{ icon: 'factory', label: '生产任务单', sub: 'Production Plan', route: ['desk', 'Production Plan'] },
			{ icon: 'chart', label: '生产汇总', sub: 'Production Plan Summary', route: ['desk', 'query-report', 'Production Plan Summary'], report: true },
		],
	},
	{
		title: '财务结算链路',
		desc: '收付款 · 费用 · 发票 · 订单利润',
		color: 'var(--erp-error)',
		light: 'var(--erp-error-light)',
		steps: [
			{ icon: 'banknote', label: '收付款', sub: 'Payment Entry · 收款/付款管理', route: ['desk', 'Payment Entry'] },
			{ icon: 'doc', label: '费用报销', sub: '费用管理 · 审批受控', route: ['desk', 'Expense Reimbursement'], badge: 'General ERP' },
			{ icon: 'file', label: '发票管理', sub: 'Sales Invoice', route: ['desk', 'Sales Invoice'] },
			{ icon: 'trend', label: '订单利润', sub: '订单利润报表', route: ['desk', 'query-report', '订单利润'], report: true },
		],
	},
];

const MASTER = [
	{ icon: 'anchor', label: '港口', note: '出运明细单 · 装运港/卸货港', route: ['desk', 'Port'], badge: 'General ERP' },
	{ icon: 'globe', label: '贸易术语', note: 'Incoterms · 订单/出运用', route: ['desk', 'Incoterms'], badge: 'General ERP' },
	{ icon: 'hash', label: 'HS 编码', note: '物料报关编码 · 海关商品', route: ['desk', 'HS Code'], badge: 'General ERP' },
	{ icon: 'sliders', label: '系统参数', note: '全局行为参数', route: ['desk', 'System Parameter'], badge: 'General ERP' },
];

const MARKETING = [
	{ icon: 'target', label: '商机', note: '商机统计 · 丢失商机', route: ['desk', 'Opportunity'] },
	{ icon: 'megaphone', label: '营销活动', note: 'Campaign · 营销计划', route: ['desk', 'Campaign'] },
	{ icon: 'mail', label: '邮件群发', note: '群发邮件 · 效果分析', plan: true, badge: '规划中' },
];

const OA = [
	{ icon: 'doc', label: '文件管理', note: 'OA 文档', route: ['desk', 'Note'] },
	{ icon: 'building', label: '部门', note: '部门管理', route: ['desk', 'HR Department'] },
	{ icon: 'building', label: '岗位', note: '岗位管理', route: ['desk', 'Designation'] },
	{ icon: 'shield', label: '角色权限', note: '岗位与权限', route: ['desk', 'Role'] },
	{ icon: 'user', label: '用户参数', note: 'User', route: ['desk', 'User'] },
	{ icon: 'building', label: '企业信息', note: 'Company', route: ['desk', 'company'] },
];

const REPORTS = [
	{ label: '外销统计', note: '出口销售', route: ['desk', 'query-report', '外销统计'] },
	{ label: '订单利润', note: '订单维度利润', route: ['desk', 'query-report', '订单利润'] },
	{ label: '产品统计', note: '产品维度', route: ['desk', 'query-report', '产品统计'] },
	{ label: '采购统计', note: '采购维度', route: ['desk', 'query-report', '采购统计'] },
	{ label: '收款统计', note: '收款维度', route: ['desk', 'query-report', '收款统计'] },
	{ label: '付款统计', note: '付款维度', route: ['desk', 'query-report', '付款统计'] },
	{ label: '费用统计', note: '费用维度', route: ['desk', 'query-report', '费用统计'] },
];

const PLATFORM = [
	{ icon: 'home', label: '工作台', note: 'Desk 首页 · 业务数据', route: ['desk'] },
	{ icon: 'clock', label: '待处理任务', note: 'ToDo', route: ['desk', 'ToDo'] },
	{ icon: 'search', label: '全局搜索', note: '内置 · ⌘K 快捷键', noroute: true, badge: '内置' },
	{ icon: 'mail', label: '沟通记录', note: 'Communication', route: ['desk', 'Communication'] },
	{ icon: 'mail', label: '邮件', note: '邮箱 · 收发/审批邮件', plan: true, badge: '规划中' },
];


/* 路由跳转：doctype 列表路由必须是小写 slug（frappe 路由表按 slug 匹配），其余保持原样 */
function go(route) {
	if (route.length === 2) {
		frappe.set_route('desk', frappe.router.slug(route[1]));
	} else {
		frappe.set_route(...route);
	}
}

function makeHead() {
	const el = document.createElement('div');
	el.className = 'business-flow-head';
	el.innerHTML = `
		<div>
			<div class="business-flow-title">外贸业务流程总览</div>
			<div class="business-flow-sub">功能清单 → 核心业务流程地图 · 点击任意节点/卡片跳转到对应单据（虚线为报表/规划中）</div>
		</div>
		<div class="business-flow-legend">
			<span class="lg"><span class="dot" style="background: var(--erp-info)"></span>销售</span>
			<span class="lg"><span class="dot" style="background: var(--erp-success)"></span>采购检验</span>
			<span class="lg"><span class="dot" style="background: #0fc6c2"></span>库存</span>
			<span class="lg"><span class="dot" style="background: #722ed1"></span>生产</span>
			<span class="lg"><span class="dot" style="background: var(--erp-error)"></span>财务</span>
			<span class="lg"><span class="dot" style="background: var(--erp-warning)"></span>审批流</span>
			<span class="lg"><span class="dot" style="background: var(--erp-text-3)"></span>支撑数据</span>
		</div>`;
	return el;
}

function makeCard(no, title, desc, color, light) {
	const card = document.createElement('div');
	card.className = 'flow-card';
	card.style.setProperty('--lane-color', color);
	card.style.setProperty('--lane-light', light);
	card.innerHTML = `
		<div class="flow-card-head">
			<span class="flow-card-no" style="background: ${color}">${no}</span>
			<span class="flow-card-title">${title}</span>
			<span class="flow-card-desc">${desc}</span>
		</div>`;
	return card;
}

function makeLaneCard(no, lane) {
	const card = makeCard(no, lane.title, lane.desc, lane.color, lane.light);
	const steps = document.createElement('div');
	steps.className = 'flow-steps';
	lane.steps.forEach((s, i) => {
		steps.appendChild(makeStep(s, lane));
		if (i < lane.steps.length - 1) {
			const a = document.createElement('span');
			a.className = 'flow-arrow';
			a.innerHTML = ICONS.arrow;
			steps.appendChild(a);
		}
	});
	card.appendChild(steps);
	return card;
}

function makeStep(s, lane) {
	const el = document.createElement('a');
	el.className = 'flow-node' + (s.report ? ' is-report' : '');
	el.href = '#';
	el.style.setProperty('--lane-color', lane.color);
	el.style.setProperty('--lane-light', lane.light);
	el.innerHTML = `
		${s.badge || s.report ? `<span class="node-badge${s.report ? ' rep' : ''}">${s.badge || '报表'}</span>` : ''}
		<span class="node-icon">${ICONS[s.icon]}</span>
		<span class="node-text">
			<span class="node-label">${s.label}</span>
			<span class="node-sub">${s.sub}</span>
		</span>`;
	el.addEventListener('click', (e) => {
		e.preventDefault();
		go(s.route);
	});
	return el;
}

function makeWorkflowCard() {
	const card = makeCard(
		'6', '费用报销审批流', '费用报销单的状态机（Workflow：费用报销审批）',
		'var(--erp-warning)', 'var(--erp-warning-light)'
	);
	const g = document.createElement('div');
	g.className = 'wf-grid';

	const state = (cls, icon, label, route) => {
		const d = document.createElement('div');
		d.className = `wf-state ${cls}`;
		d.innerHTML = `${ICONS[icon]}<span>${label}</span>`;
		if (route) {
			d.style.cursor = 'pointer';
			d.addEventListener('click', () => go(route));
		}
		return d;
	};
	const hArr = (action, down) => {
		const d = document.createElement('div');
		d.className = 'wf-arrow' + (down ? ' wf-arrow-down' : '');
		d.innerHTML = `${down ? ICONS.downarrow : ICONS.arrow}<span class="wf-action">${action}</span>`;
		return d;
	};
	const empty = () => {
		const d = document.createElement('span');
		g.appendChild(d);
	};

	const ER = ['desk', 'Expense Reimbursement'];
	g.appendChild(state('st-draft', 'doc', '草稿', ER));
	g.appendChild(hArr('提交审批'));
	g.appendChild(state('st-pending', 'clock', '审批中', ER));
	g.appendChild(hArr('审批'));
	g.appendChild(state('st-approved', 'checkc', '已审批', ER));
	empty(); empty();
	g.appendChild(hArr('驳回', true));
	empty(); empty();
	g.appendChild(state('st-rejected', 'x', '已驳回', ER));
	g.appendChild(hArr('重新提交'));
	g.appendChild(state('st-ref', 'clock', '回到审批中', null));

	const note = document.createElement('div');
	note.className = 'wf-note';
	note.innerHTML = '单据提交后进入 <b>审批中</b>，审批通过则 <b>已审批</b>（单据受控不可再改）；驳回后可修改并 <b>重新提交</b>。审批操作：提交审批 / 审批 / 驳回 / 重新提交。';
	card.appendChild(g);
	card.appendChild(note);
	return card;
}

function makeChipCard(no, title, desc, color, light, items, icon) {
	const card = makeCard(no, title, desc, color, light);
	const row = document.createElement('div');
	row.className = 'chip-row';
	items.forEach((s) => {
		const el = document.createElement('a');
		el.className = 'flow-chip' + (s.plan ? ' is-plan' : '') + (s.noroute ? ' is-static' : '');
		el.href = '#';
		el.style.setProperty('--lane-color', color);
		el.style.setProperty('--lane-light', light);
		el.innerHTML = `
			<span class="chip-icon">${ICONS[s.icon || icon]}</span>
			<span class="chip-text">
				<span class="chip-label">${s.label}${s.badge ? ` <span class="chip-badge${s.plan ? ' plan' : ''}">${s.badge}</span>` : ''}</span>
				<span class="chip-note">${s.note}</span>
			</span>
			${!s.plan && !s.noroute ? `<span class="chip-go">${ICONS.go}</span>` : ''}`;
		if (!s.plan && !s.noroute) {
			el.addEventListener('click', (e) => {
				e.preventDefault();
				go(s.route);
			});
		}
		row.appendChild(el);
	});
	card.appendChild(row);
	return card;
}

function make(wrapper) {
	const wrap = document.createElement('div');
	wrap.className = 'business-flow-wrap';

	wrap.appendChild(makeHead());
	LANES.forEach((lane, i) => wrap.appendChild(makeLaneCard(i + 1, lane)));
	wrap.appendChild(makeWorkflowCard());
	wrap.appendChild(makeChipCard(7, '营销与获客', '商机培育 · 邮件营销', '#eb2f96', 'rgba(235, 47, 150, 0.12)', MARKETING, 'target'));
	wrap.appendChild(makeChipCard(8, '基础数据支撑', '销售/采购链路共用的主数据', 'var(--erp-text-3)', 'var(--erp-bg-muted)', MASTER, 'doc'));
	wrap.appendChild(makeChipCard(9, 'OA 与系统设置', '文档 · 组织 · 权限 · 参数', 'var(--erp-text-3)', 'var(--erp-bg-muted)', OA, 'doc'));
	wrap.appendChild(makeChipCard(10, '报表中心', '经营结果分析', 'var(--erp-info)', 'var(--erp-info-light)', REPORTS, 'chart'));
	wrap.appendChild(makeChipCard(11, '平台与协作', '工作台 · 搜索 · 沟通', 'var(--erp-text-3)', 'var(--erp-bg-muted)', PLATFORM, 'doc'));

	wrapper.append(wrap);
}

/* 页面注册：frappe.views.Page 构造时 eval 本脚本，随后触发 wrapper.on_page_load(wrapper) */
frappe.pages['business-flow'].on_page_load = function (wrapper) {
	make(wrapper);
};
