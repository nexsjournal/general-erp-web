/* 业务流程展示页（演示用）：按功能清单梳理核心业务流程，串联现有单据 */
/* BF_PAGE_V8 */

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
	phone: I('<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/>'),
	calendar: I('<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>'),
	inbox: I('<path d="M22 12h-6l-2 3h-4l-2-3H2"/><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/>'),
	search: I('<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>'),
	trend: I('<path d="m3 17 6-6 4 4 8-8"/><path d="M14 7h7v7"/>'),
	truck: I('<rect x="1" y="6" width="14" height="10" rx="1.5"/><path d="M15 9h4l3 3v4h-7V9z"/><circle cx="6" cy="18.5" r="1.8"/><circle cx="18" cy="18.5" r="1.8"/>'),
	share: I('<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.6 13.5 6.8 4M15.4 6.5l-6.8 4"/>'),
};

/* ---------- 业务数据：功能清单 → 核心业务流程 ---------- */

const LANES = [
	{
		title: __('标准销售主链路'),
		desc: __('非外贸销售 · 客户 → 商机 → 报价 → 订单 → 交货 → 开票 → 收款 → 利润'),
		color: '#fa8c16',
		light: 'rgba(250, 140, 22, 0.12)',
		steps: [
			{ icon: 'user', label: __('客户'), sub: __('我的客户 · 公海 · 热点 · 移交'), route: ['desk', 'Customer'] },
			{ icon: 'phone', label: __('客户跟进'), sub: __('电话/邮件/拜访 · 公海回收依据'), route: ['desk', 'customer-follow-up'], badge: 'ERP' },
			{ icon: 'target', label: __('商机'), sub: __('待批复 · 已批复 · 待回复 · 商机统计'), route: ['desk', 'Opportunity'] },
			{ icon: 'file', label: __('报价单'), sub: __('报价管理'), route: ['desk', 'Quotation'] },
			{ icon: 'clipboard', label: __('销售订单'), sub: __('内贸订单 · 不走出运/单证'), route: ['desk', 'Sales Order'] },
			{ icon: 'box', label: __('交货单'), sub: __('交货单 · 销售出库'), route: ['desk', 'Delivery Note'] },
			{ icon: 'file', label: __('销售发票'), sub: __('销售发票 · 开票'), route: ['desk', 'Sales Invoice'] },
			{ icon: 'banknote', label: __('收款'), sub: __('收款管理 · 收付款单'), route: ['desk', 'Payment Entry'] },
			{ icon: 'trend', label: __('订单利润'), sub: __('订单维度利润分析'), route: ['desk', 'query-report', '订单利润'], report: true },
		],
	},
	{
		title: __('外贸销售主链路'),
		desc: __('客户获取 → 商机 → 报价 → 订单 → 出运 → 单证 → 收款 → 利润'),
		color: 'var(--erp-info)',
		light: 'var(--erp-info-light)',
		steps: [
			{ icon: 'user', label: __('线索'), sub: __('网站询盘 · 分发跟踪 · 转客户'), route: ['desk', 'Lead'] },
		{ icon: 'user', label: __('客户'), sub: __('我的客户 · 公海 · 热点 · 移交'), route: ['desk', 'Customer'] },
		{ icon: 'phone', label: __('客户跟进'), sub: __('电话/邮件/拜访 · 公海回收依据'), route: ['desk', 'customer-follow-up'], badge: 'ERP' },
			{ icon: 'user', label: __('客户 360'), sub: __('全景视图 · 共享 · 合并 · 移交'), route: ['desk', 'customer-360'], badge: 'ERP' },
			{ icon: 'target', label: __('商机'), sub: __('待批复 · 已批复 · 待回复 · 商机统计'), route: ['desk', 'Opportunity'] },
			{ icon: 'file', label: __('报价单'), sub: __('报价管理'), route: ['desk', 'Quotation'] },
			{ icon: 'clipboard', label: __('销售订单'), sub: __('外贸订单'), route: ['desk', 'Sales Order'] },
			{ icon: 'anchor', label: __('出运明细单'), sub: __('装运港/卸货港 · 贸易术语 · 出运明细'), route: ['desk', 'Export Shipment'], badge: 'ERP' },
			{ icon: 'filecheck', label: __('外贸单证'), sub: __('单证制作 · 出口报关'), route: ['desk', 'Trade Document'], badge: 'ERP' },
			{ icon: 'banknote', label: __('收款'), sub: __('收款管理 · 收付款单'), route: ['desk', 'Payment Entry'] },
			{ icon: 'trend', label: __('订单利润'), sub: __('订单维度利润分析'), route: ['desk', 'query-report', '订单利润'], report: true },
		],
	},
	{
		title: __('采购与来料检验'),
		desc: __('供应商 → 采购 → 入库 → 来料检验'),
		color: 'var(--erp-success)',
		light: 'var(--erp-success-light)',
		steps: [
			{ icon: 'users', label: __('供应商'), sub: __('供应商主数据'), route: ['desk', 'Supplier'] },
			{ icon: 'clipboardcheck', label: __('采购订单'), sub: __('下达 PO'), route: ['desk', 'Purchase Order'] },
			{ icon: 'package', label: __('采购入库'), sub: 'Purchase Receipt', route: ['desk', 'Purchase Receipt'] },
			{ icon: 'searchcheck', label: __('来料验货单'), sub: __('检验人 · 验货明细 · 结论'), route: ['desk', 'Inspection Order'], badge: 'ERP' },
			{ icon: 'box', label: __('物料'), sub: __('产品库 · HS 编码'), route: ['desk', 'Item'] },
		],
	},
	{
		title: __('库存管理链路'),
		desc: __('入库 → 库存余额 → 出库 → 统计 / 预警'),
		color: '#0fc6c2',
		light: 'rgba(15, 198, 194, 0.12)',
		steps: [
			{ icon: 'box', label: __('入库'), sub: __('入库单 · 其他入库'), route: ['desk', 'Stock Entry'] },
			{ icon: 'archive', label: __('库存余额'), sub: __('库存汇总'), route: ['desk', 'stock-balance'] },
			{ icon: 'box', label: __('出库'), sub: __('交货单 · 销售出库'), route: ['desk', 'Delivery Note'] },
			{ icon: 'chart', label: __('库存统计'), sub: __('库存余额报表'), route: ['desk', 'query-report', 'Stock Balance'], report: true },
			{ icon: 'chart', label: __('库存预警'), sub: __('低于再订货点 · 库存预警报表'), route: ['desk', 'query-report', '库存预警'], report: true },
		],
	},
	{
		title: __('生产链路'),
	 desc: __('生产任务单 → 生产进度'),
		color: '#722ed1',
		light: 'rgba(114, 46, 209, 0.12)',
		steps: [
			{ icon: 'factory', label: __('生产任务单'), sub: __('生产任务单'), route: ['desk', 'Production Plan'] },
			{ icon: 'chart', label: __('生产汇总'), sub: __('生产汇总报表'), route: ['desk', 'query-report', 'Production Plan Summary'], report: true },
		],
	},
	{
		title: __('财务结算链路'),
		desc: __('收付款 · 费用 · 发票 · 订单利润'),
		color: 'var(--erp-error)',
		light: 'var(--erp-error-light)',
		steps: [
			{ icon: 'banknote', label: __('收付款'), sub: __('收款/付款管理'), route: ['desk', 'Payment Entry'] },
			{ icon: 'doc', label: __('费用报销'), sub: __('费用管理 · 审批受控'), route: ['desk', 'Expense Reimbursement'], badge: 'ERP' },
			{ icon: 'file', label: __('发票管理'), sub: 'Sales Invoice', route: ['desk', 'Sales Invoice'] },
			{ icon: 'trend', label: __('订单利润'), sub: __('订单利润报表'), route: ['desk', 'query-report', '订单利润'], report: true },
		],
	},
];

const MASTER = [
	{ icon: 'anchor', label: __('港口'), note: __('出运明细单 · 装运港/卸货港'), route: ['desk', 'Port'], badge: 'ERP' },
	{ icon: 'globe', label: __('贸易术语'), note: __('国际贸易术语 · 订单/出运用'), route: ['desk', 'Incoterms'], badge: 'ERP' },
	{ icon: 'hash', label: __('HS 编码'), note: __('物料报关编码 · 海关商品'), route: ['desk', 'HS Code'], badge: 'ERP' },
	{ icon: 'sliders', label: __('系统参数'), note: __('全局行为参数'), route: ['desk', 'System Parameter'], badge: 'ERP' },
	{ icon: 'banknote', label: __('币种汇率'), note: __('今日汇率 · 工作台数字卡'), route: ['desk', 'currency-exchange-rate'], badge: 'ERP' },
	{ icon: 'truck', label: __('服务商'), note: __('货代 · 船公司 · 报关行'), route: ['desk', 'service-provider'], badge: 'ERP' },
	{ icon: 'sliders', label: __('统计设置'), note: __('公海天数 · 报表订阅 · 权限矩阵'), route: ['desk', 'statistics-settings'], badge: 'ERP' },
	{ icon: 'globe', label: __('区域设置'), note: __('语言/时区/日期 · 中英文切换'), route: ['desk', 'regional-settings'], badge: 'ERP' },
];

const MARKETING = [
	{ icon: 'target', label: __('商机'), note: __('商机统计 · 丢失商机'), route: ['desk', 'Opportunity'] },
	{ icon: 'megaphone', label: __('营销活动'), note: __('营销活动 · 营销计划'), route: ['desk', 'Campaign'] },
	{ icon: 'megaphone', label: __('邮件群发'), note: __('客户群发 · 模板变量 · 发送统计'), route: ['desk', 'bulk-email'] },
	{ icon: 'file', label: __('邮件模板'), note: __('营销主题 · {{customer_name}} 变量'), route: ['desk', 'email-template'], badge: 'ERP' },
	{ icon: 'share', label: __('线索分发'), note: __('分发记录 · 留痕追溯'), route: ['desk', 'lead-distribution-log'], badge: 'ERP' },
	{ icon: 'globe', label: __('网站留言'), note: __('官网表单 → 线索 · 嵌入代码'), route: ['desk', 'website-lead-code'], badge: 'ERP' },
];

const OA = [
	{ icon: 'doc', label: __('文件管理'), note: __('文档管理'), route: ['desk', 'Note'] },
	{ icon: 'bell', label: __('公告'), note: __('通知公告 · 置顶/有效期'), route: ['desk', 'announcement'], badge: 'ERP' },
	{ icon: 'building', label: __('部门'), note: __('组织模块未启用 · 规划中'), noroute: true, badge: __('规划中') },
	{ icon: 'checkc', label: __('工作检查'), note: __('每日/每周自检 · 待办提醒'), route: ['desk', 'work-check'], badge: 'ERP' },
	{ icon: 'calendar', label: __('工作日历'), note: __('节假日 · 跟进 · 出运 · 检查'), route: ['desk', 'work-calendar'], badge: 'ERP' },
	{ icon: 'building', label: __('岗位'), note: __('岗位管理'), route: ['desk', 'Designation'] },
	{ icon: 'shield', label: __('角色权限'), note: __('岗位与权限'), route: ['desk', 'Role'] },
	{ icon: 'user', label: __('用户参数'), note: 'User', route: ['desk', 'User'] },
	{ icon: 'building', label: __('企业信息'), note: 'Company', route: ['desk', 'company'] },
];

const REPORTS = [
	{ label: __('外销统计'), note: __('出口销售'), route: ['desk', 'query-report', '外销统计'] },
	{ label: __('出运统计'), note: __('出运维度 · 港口/柜量'), route: ['desk', 'query-report', '出运统计'] },
	{ label: __('订单利润'), note: __('订单维度利润'), route: ['desk', 'query-report', '订单利润'] },
	{ label: __('产品统计'), note: __('产品维度'), route: ['desk', 'query-report', '产品统计'] },
	{ label: __('采购统计'), note: __('采购维度'), route: ['desk', 'query-report', '采购统计'] },
	{ label: __('收款统计'), note: __('收款维度'), route: ['desk', 'query-report', '收款统计'] },
	{ label: __('付款统计'), note: __('付款维度'), route: ['desk', 'query-report', '付款统计'] },
	{ label: __('费用统计'), note: __('费用维度'), route: ['desk', 'query-report', '费用统计'] },
	{ label: __('客户统计'), note: __('公海 · 热点 · 跟进'), route: ['desk', 'query-report', '客户统计'] },
	{ label: __('线索统计'), note: __('分发 · 转化率'), route: ['desk', 'query-report', '线索统计'] },
	{ label: __('商机统计'), note: __('批复状态 · 赢单率'), route: ['desk', 'query-report', '商机统计'] },
	{ label: __('员工业绩排行'), note: __('客户 · 订单 · 跟进排名'), route: ['desk', 'query-report', '员工业绩排行'] },
	{ label: __('邮件统计'), note: __('文件夹 · 群发成功率'), route: ['desk', 'query-report', '邮件统计'] },
	{ label: __('员工工作情况表'), note: __('员工工作量 · 跟进/邮件/检查'), route: ['desk', 'query-report', '员工工作情况表'] },
];

const PLATFORM = [
	{ icon: 'home', label: __('工作台'), note: __('工作台首页 · 业务数据'), route: ['desk', 'ERP工作台'] },
	{ icon: 'clock', label: __('待处理任务'), note: __('待办事项'), route: ['desk', 'ToDo'] },
	{ icon: 'search', label: __('全局搜索'), note: __('内置 · ⌘K 快捷键'), noroute: true, badge: __('内置') },
	{ icon: 'mail', label: __('沟通记录'), note: __('沟通记录'), route: ['desk', 'Communication'] },
	{ icon: 'mail', label: __('邮件中心'), note: __('待处理 · 收件箱 · 草稿箱'), route: ['desk', 'mail-center'] },
	{ icon: 'inbox', label: __('邮箱账号'), note: __('IMAP 接入 · 定时收信 · 打开/点击跟踪'), route: ['desk', 'mail-account'], badge: 'ERP' },
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
			<div class="business-flow-title">${__("业务流程总览")}</div>
			<div class="business-flow-sub">${__("功能清单 → 核心业务流程地图 · 点击任意节点/卡片跳转到对应单据（虚线为报表/内置）")}</div>
		</div>
		<div class="business-flow-legend">
			<span class="lg"><span class="dot" style="background: #fa8c16"></span>${__('标准销售')}</span>
			<span class="lg"><span class="dot" style="background: var(--erp-info)"></span>${__('销售')}</span>
			<span class="lg"><span class="dot" style="background: var(--erp-success)"></span>${__('采购检验')}</span>
			<span class="lg"><span class="dot" style="background: #0fc6c2"></span>${__('库存')}</span>
			<span class="lg"><span class="dot" style="background: #722ed1"></span>${__('生产')}</span>
			<span class="lg"><span class="dot" style="background: var(--erp-error)"></span>${__('财务')}</span>
			<span class="lg"><span class="dot" style="background: var(--erp-warning)"></span>${__('审批流')}</span>
			<span class="lg"><span class="dot" style="background: var(--erp-text-3)"></span>${__('支撑数据')}</span>
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
		${s.badge || s.report ? `<span class="node-badge${s.report ? ' rep' : ''}">${s.badge || __('报表')}</span>` : ''}
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
		'6', __('费用报销审批流'), __('费用报销单的状态流转（工作流：费用报销审批）'),
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
	g.appendChild(state('st-draft', 'doc', __('草稿'), ER));
	g.appendChild(hArr(__('提交审批')));
	g.appendChild(state('st-pending', 'clock', __('审批中'), ER));
	g.appendChild(hArr(__('审批')));
	g.appendChild(state('st-approved', 'checkc', __('已审批'), ER));
	empty(); empty();
	g.appendChild(hArr(__('驳回'), true));
	empty(); empty();
	g.appendChild(state('st-rejected', 'x', __('已驳回'), ER));
	g.appendChild(hArr(__('重新提交')));
	g.appendChild(state('st-ref', 'clock', __('回到审批中'), null));

	const note = document.createElement('div');
	note.className = 'wf-note';
	note.innerHTML = `${__('单据提交后进入')} <b>${__('审批中')}</b>，${__('审批通过则')} <b>${__('已审批')}</b>${__('（单据受控不可再改）')}；${__('驳回后可修改并')} <b>${__('重新提交')}</b>。${__('审批操作：提交审批 / 审批 / 驳回 / 重新提交。')}`;
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
			<span class="chip-icon">${ICONS[s.icon || icon] || ICONS.box}</span>
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
	wrap.appendChild(makeChipCard(7, __('营销与获客'), __('商机培育 · 邮件营销'), '#eb2f96', 'rgba(235, 47, 150, 0.12)', MARKETING, 'target'));
	wrap.appendChild(makeChipCard(8, __('基础数据支撑'), __('销售/采购链路共用的主数据'), 'var(--erp-text-3)', 'var(--erp-bg-muted)', MASTER, 'doc'));
	wrap.appendChild(makeChipCard(9, __('OA 与系统设置'), __('文档 · 组织 · 权限 · 检查 · 日历'), 'var(--erp-text-3)', 'var(--erp-bg-muted)', OA, 'doc'));
	wrap.appendChild(makeChipCard(10, __('报表中心'), __('经营结果分析'), 'var(--erp-info)', 'var(--erp-info-light)', REPORTS, 'chart'));
	wrap.appendChild(makeChipCard(11, __('平台与协作'), __('工作台 · 搜索 · 沟通 · 邮箱'), 'var(--erp-text-3)', 'var(--erp-bg-muted)', PLATFORM, 'doc'));

	wrapper.append(wrap);
}

/* 页面注册：frappe.views.Page 构造时 eval 本脚本，随后触发 wrapper.on_page_load(wrapper) */
frappe.pages['business-flow'].on_page_load = function (wrapper) {
	make(wrapper);
};
