// 帮助中心：左侧模块导航 + 右侧分步操作说明（一看就会）
const HELP_DATA = {
 '销售管理': {
  desc: '从客户到收款的完整销售过程',
  steps: [
   ['1. 建客户', '左侧「客户管理」→ 客户 → 添加客户，填名称/联系方式/区域'],
   ['2. 跟进与商机', '打开客户 → 加跟进记录；成熟客户点「转商机」'],
   ['3. 做报价单', '销售管理 → 报价单 → 添加，选客户+商品+价格，保存'],
   ['4. 转销售订单', '报价单列表 → 勾选 → 转换 → 销售订单'],
   ['5. 交货', '销售订单 → 转换 → 交货单 → 提交（库存自动扣减）'],
   ['6. 开票', '交货单 → 转换 → 销售发票 → 提交'],
   ['7. 收款', '销售发票 → 创建 → 付款申请/收款单，填收款金额+账户'],
   ['8. 看利润', '报表中心 → 订单利润，看每张单赚了多少'],
  ]
 },
 '采购管理': {
  desc: '从供应商到验货的完整采购过程',
  steps: [
   ['1. 建供应商', '采购管理 → 供应商 → 添加'],
   ['2. 采购订单', '采购管理 → 采购订单 → 添加，选供应商+商品+数量'],
   ['3. 收货入库', '采购订单 → 转换 → 采购入库 → 提交（库存自动增加）'],
   ['4. 来料检验', '需要质检的商品 → 创建检验单 → 判定合格/不合格'],
   ['5. 付款', '采购发票 → 创建 → 付款单'],
  ]
 },
 '库存管理': {
  desc: '看库存、调库存、防超卖',
  steps: [
   ['1. 查库存', '库存管理 → 库存查询，按商品/仓库看现有数量'],
   ['2. 出入库', '入库单/出库单 直接开单；销售交货/采购收货会自动产生'],
   ['3. 库存流水', '库存流水 看每张单的进出明细'],
   ['4. 安全库存', '商品上设安全库存，低于自动预警'],
  ]
 },
 '财务管理': {
  desc: '收付款、费用、发票、利润',
  steps: [
   ['1. 收款', '销售发票 → 创建 → 收款单，关联客户+金额'],
   ['2. 付款', '采购发票 → 创建 → 付款单，关联供应商+金额'],
   ['3. 费用报销', '费用报销 → 添加 → 走审批流程'],
   ['4. 发票管理', '收票/开票列表，核销对账'],
   ['5. 订单利润', '报表中心 → 订单利润，自动算每单毛利'],
  ]
 },
 '客户管理': {
  desc: '客户全生命周期',
  steps: [
   ['1. 我的客户', '看分配给自己的客户，按跟进状态筛选'],
   ['2. 跟进记录', '打开客户 → 跟进记录 → 加一条（电话/拜访/邮件）'],
   ['3. 360视图', '客户 → 360 看全部往来（订单/发票/欠款/跟进）'],
   ['4. 公海', '长期未跟进客户自动回公海，其他人可认领'],
   ['5. 移交/共享', '客户详情页 → 移交/共享按钮'],
  ]
 },
 '产品管理': {
  desc: '商品资料维护',
  steps: [
   ['1. 建商品', '产品管理 → 商品 → 添加，填名称/编码/单位/价格'],
   ['2. 商品组', '按类别建商品组，方便筛选'],
   ['3. 单位与规格', '商品里设计量单位（个/箱/千克）'],
   ['4. 海关编码', '外贸商品填海关 HS 编码'],
  ]
 },
 '邮件中心': {
  desc: '邮箱收发+群发营销',
  steps: [
   ['1. 接邮箱', '邮件中心 → 邮箱账号 → 添加（IMAP/SMTP）'],
   ['2. 收发', '邮件工作台 像 QQ 邮箱一样收发'],
   ['3. 群发', '群发邮件 → 选客户群+模板 → 发送，自动追踪打开/点击'],
  ]
 },
 '外贸管理': {
  desc: '出运、单证、基础数据',
  steps: [
   ['1. 出运明细', '销售订单交货后 → 创建出运明细单（装箱/船期）'],
   ['2. 做单证', '出运明细 → 生成 PI/CI/PL（中英文打印）'],
   ['3. 基础数据', '海关编码/贸易术语/港口/服务商 先维护好'],
  ]
 },
 '组织管理': {
  desc: '人员、角色、权限、审批',
  steps: [
   ['1. 加员工', '组织管理 → 员工 → 添加，关联部门'],
   ['2. 设角色', '角色 → 给用户勾选能用的模块权限'],
   ['3. 配审批', '工作流 → 给某单据设审批节点（谁审）'],
   ['4. 调权限', '管理员随时给用户加/减角色，立即生效'],
  ]
 },
 '报表中心': {
  desc: '经营数据+业务流程总览',
  steps: [
   ['1. 业务流程', '报表中心 → 业务流程，六大主链路总览图'],
   ['2. 销售报表', '按客户/商品/业务员统计销售'],
   ['3. 库存报表', '库存余额/进出流水'],
   ['4. 收付款统计', '按期间统计收付款'],
  ]
 },
 '系统设置': {
  desc: '公司、用户、备份、流程配置',
  steps: [
   ['1. 公司', '系统设置 → 公司，填公司名称/币种'],
   ['2. 用户', '用户 → 添加/禁用账号'],
   ['3. 流程配置', '数据与备份 → 流程配置，改每个模块的流程步骤'],
   ['4. 数据备份', '数据与备份 → 数据备份，一键备份/下载，每日自动'],
  ]
 },
 '工作台': {
  desc: '登录后第一个页面',
  steps: [
   ['1. 看概览', '今日销售额/应收账款/待办/汇率 一目了然'],
   ['2. 点模块', '点任意模块卡片进入对应功能'],
   ['3. 待办', '待办里集中显示要处理的单据'],
  ]
 }
};

const HELP_PAGE = function (wrapper) {
	const modules = Object.keys(HELP_DATA);
	const el = document.createElement('div');
	el.className = 'help-center-wrap';
	el.innerHTML = `
		<div class="hc-layout">
			<div class="hc-nav">
				${modules.map((m, i) => `<div class="hc-nav-item ${i===0?'active':''}" data-mod="${m}">${m}</div>`).join('')}
			</div>
			<div class="hc-content">
				<div class="hc-title"></div>
				<div class="hc-desc"></div>
				<div class="hc-steps"></div>
			</div>
		</div>
	`;
	wrapper.append(el);

	const titleEl = el.querySelector('.hc-title');
	const descEl = el.querySelector('.hc-desc');
	const stepsEl = el.querySelector('.hc-steps');

	function render(mod) {
		const d = HELP_DATA[mod];
		titleEl.textContent = mod;
		descEl.textContent = d.desc;
		stepsEl.innerHTML = d.steps.map((s, i) => `
			<div class="hc-step">
				<div class="hc-step-no">${i+1}</div>
				<div class="hc-step-body">
					<div class="hc-step-t">${s[0]}</div>
					<div class="hc-step-d">${s[1]}</div>
				</div>
			</div>
		`).join('');
	}
	modules[0] && render(modules[0]);

	el.querySelectorAll('.hc-nav-item').forEach(item => {
		item.addEventListener('click', () => {
			el.querySelectorAll('.hc-nav-item').forEach(x => x.classList.remove('active'));
			item.classList.add('active');
			render(item.dataset.mod);
		});
	});
};

const hs = document.createElement('style');
hs.textContent = `
.help-center-wrap{height:100%;}
.hc-layout{display:flex;gap:0;height:calc(100vh - 80px);}
.hc-nav{width:200px;flex-shrink:0;border-right:1px solid #eee;padding:12px 0;overflow-y:auto;}
.hc-nav-item{padding:10px 18px;font-size:14px;color:#444;cursor:pointer;border-left:3px solid transparent;}
.hc-nav-item:hover{background:#f5f5f5;}
.hc-nav-item.active{background:#eef5fb;border-left-color:#2980b9;color:#2980b9;font-weight:600;}
.hc-content{flex:1;padding:24px 32px;overflow-y:auto;}
.hc-title{font-size:22px;font-weight:600;color:#222;margin-bottom:6px;}
.hc-desc{font-size:14px;color:#888;margin-bottom:24px;}
.hc-step{display:flex;gap:14px;margin-bottom:18px;align-items:flex-start;}
.hc-step-no{width:28px;height:28px;flex-shrink:0;border-radius:50%;background:#2980b9;color:#fff;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:600;}
.hc-step-body{background:#fafafa;border:1px solid #eee;border-radius:8px;padding:12px 16px;flex:1;}
.hc-step-t{font-size:15px;font-weight:600;color:#333;margin-bottom:4px;}
.hc-step-d{font-size:13.5px;color:#666;line-height:1.6;}
`;
document.head.appendChild(hs);

frappe.pages['help-center'].on_page_load = function (wrapper) {
	HELP_PAGE(wrapper);
};
