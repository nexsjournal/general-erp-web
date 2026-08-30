// 帮助中心：快速上手 + 13功能模块 + 常用操作速查 + 常见问题（金蝶式结构，一看就会）

// ===== 快速上手：3 步 =====
const STARTER = [
  { t: '第 1 步 · 认识首页', d: '登录后先看到「首页」，上面有今天的销售额、应收账款、待办、汇率，下面是一排功能模块卡片。点哪个卡片就进哪个功能。' },
  { t: '第 2 步 · 跟着流程走', d: '每个模块页顶部都有一条「流程：A → B → C」的指引条，告诉你这个模块按什么顺序操作。照着点就行，不用记。' },
  { t: '第 3 步 · 不会就看这里', d: '任何功能不会用，打开「报表中心 → 帮助中心」，左边选模块，右边一步步教你。常用操作有速查表，遇到问题有常见问题解答。' },
];

// ===== 13 功能模块详细用法 =====
const MODULES = {
 '销售管理': {
  desc: '从客户到收款的完整销售过程，外贸和内销都走这里。',
  steps: [
   ['建客户', '左侧「客户管理」→ 客户 → 新建，填名称、联系方式、区域。'],
   ['做报价单', '销售管理 → 报价单 → 新建，选客户，加商品、填数量和价格，保存。'],
   ['转销售订单', '报价单列表 → 勾选 → 转换 → 销售订单。'],
   ['交货', '销售订单 → 转换 → 交货单 → 提交。库存自动扣减。'],
   ['开票', '交货单 → 转换 → 销售发票 → 提交。'],
   ['收款', '销售发票 → 创建 → 收款单，填收款金额和账户。'],
   ['看利润', '报表中心 → 订单利润，看每张单赚了多少。'],
  ]
 },
 '采购管理': {
  desc: '从供应商到验货的完整采购过程。',
  steps: [
   ['建供应商', '采购管理 → 供应商 → 新建。'],
   ['采购订单', '采购管理 → 采购订单 → 新建，选供应商、加商品、填数量价格。'],
   ['收货入库', '采购订单 → 转换 → 采购入库 → 提交。库存自动增加。'],
   ['来料检验', '需要质检的商品 → 创建检验单 → 判定合格/不合格。'],
   ['付款', '采购发票 → 创建 → 付款单。'],
  ]
 },
 '库存管理': {
  desc: '查库存、出入库、防超卖。',
  steps: [
   ['查库存', '库存管理 → 库存查询，按商品或仓库看现有数量。'],
   ['出入库', '销售交货、采购收货会自动产生库存变动；也可手动开出库单/入库单。'],
   ['看流水', '库存流水，看每张单的进出明细。'],
   ['安全库存', '商品上设安全库存，低于自动预警。'],
  ]
 },
 '财务管理': {
  desc: '收付款、费用报销、发票、利润。',
  steps: [
   ['收款', '销售发票 → 创建 → 收款单，关联客户和金额。'],
   ['付款', '采购发票 → 创建 → 付款单，关联供应商和金额。'],
   ['费用报销', '财务管理 → 费用报销 → 新建，填日期、类型、金额，走审批。'],
   ['发票管理', '收票/开票列表，核销对账。'],
   ['订单利润', '报表中心 → 订单利润，自动算每张单的毛利。'],
   ['三大报表', '报表中心 → 试算平衡表 / 资产负债表 / 利润表，选会计年度出数。'],
  ]
 },
 '客户管理': {
  desc: '客户全生命周期管理。',
  steps: [
   ['我的客户', '看分配给自己的客户，按跟进状态筛选。'],
   ['跟进记录', '打开客户 → 跟进记录 → 加一条（电话/拜访/邮件）。'],
   ['360 视图', '客户 → 360，看全部往来：订单、发票、欠款、跟进。'],
   ['公海', '长期未跟进的客户自动回公海，其他人可认领。'],
   ['移交/共享', '客户详情页 → 移交或共享给同事。'],
  ]
 },
 '产品管理': {
  desc: '商品资料维护，传统产品和外贸产品都在这建。',
  steps: [
   ['建商品', '产品管理 → 商品 → 新建，填编码、名称、商品组、单位。'],
   ['传统产品', '办公用品等非外贸商品，填完 4 项必填就能保存，不用填海关编码。'],
   ['商品组', '按类别建商品组，方便筛选和管理。'],
   ['单位与规格', '商品里设计量单位（个/箱/千克）。'],
   ['海关编码', '外贸商品才需要，在「外贸管理 → 海关编码」里维护，不强制。'],
  ]
 },
 '邮件中心': {
  desc: '邮箱收发 + 群发营销。',
  steps: [
   ['接邮箱', '邮件中心 → 邮箱账号 → 新建，填 IMAP/SMTP 服务器信息。'],
   ['收发', '邮件工作台，像 QQ 邮箱一样收发。'],
   ['群发', '群发邮件 → 选客户群 + 模板 → 发送，自动追踪打开和点击。'],
  ]
 },
 '外贸管理': {
  desc: '出运、单证、外贸基础数据。',
  steps: [
   ['出运明细', '销售订单交货后 → 创建出运明细单（装箱、船期）。'],
   ['做单证', '出运明细 → 生成 PI/CI/PL（中英文对照打印）。'],
   ['基础数据', '海关编码 / 贸易术语 / 港口 / 服务商，先维护好再出单。'],
  ]
 },
 '生产管理': {
  desc: '生产工单和进度（一般客户可不用）。',
  steps: [
   ['建 BOM', '产品管理 → BOM，定义成品由哪些原料组成。'],
   ['开工单', '生产管理 → 生产工单 → 新建，选 BOM、填计划数量。'],
   ['跟进度', '工单列表看状态：未开始/生产中/已完成。'],
  ]
 },
 '组织管理': {
  desc: '人员、部门、角色、权限、审批。',
  steps: [
   ['加员工', '组织管理 → 员工 → 新建，关联部门和岗位。'],
   ['设角色', '角色 → 给用户勾选能用的模块权限。'],
   ['配审批', '工作流 → 给某单据设审批节点（谁来审）。'],
   ['调权限', '管理员随时给用户加/减角色，立即生效。'],
  ]
 },
 '报表中心': {
  desc: '经营数据 + 业务流程总览 + 帮助中心。',
  steps: [
   ['业务流程', '报表中心 → 业务流程，六大主链路总览图。'],
   ['销售报表', '按客户/商品/业务员统计销售。'],
   ['库存报表', '库存余额、进出流水、库存预警。'],
   ['收付款统计', '按期间统计收付款。'],
   ['帮助中心', '报表中心 → 帮助中心，所有功能的操作说明（就是这页）。'],
  ]
 },
 '系统设置': {
  desc: '公司、用户、备份、流程配置。',
  steps: [
   ['公司', '系统设置 → 公司，填公司名称、币种。'],
   ['用户', '用户 → 新建/禁用账号。'],
   ['流程配置', '数据与备份 → 流程配置，改每个模块的流程步骤和顺序。'],
   ['数据备份', '数据与备份 → 数据备份，一键备份/下载，每天凌晨自动备份。'],
  ]
 },
 '工作台': {
  desc: '登录后第一个页面。',
  steps: [
   ['看概览', '今日销售额、应收账款、待办、汇率，一目了然。'],
   ['点模块', '点任意模块卡片进入对应功能。'],
   ['待办', '待办里集中显示要处理的单据。'],
  ]
 },
};

// ===== 常用操作速查表 =====
const QUICK = [
  ['新建任意单据', '进对应模块列表页 → 点「新建」按钮 → 填必填项（带 * 的）→ 保存'],
  ['一张单转下一张', '在源单据列表勾选 → 顶部「转换」→ 选目标单据类型'],
  ['提交/撤回单据', '单据列表勾选 → 「提交」；已提交的点「取消」撤回（需未做下游）'],
  ['改流程顺序', '系统设置 → 数据与备份 → 流程配置 → 选中模块 → 拖步骤调顺序'],
  ['备份数据', '系统设置 → 数据与备份 → 数据备份 → 立即备份 → 下载文件'],
  ['给用户加权限', '系统设置 → 用户 → 选中人 → 角色里勾选模块 → 保存'],
  ['查某客户的账', '客户管理 → 打开客户 → 360，看订单/发票/欠款'],
  ['换语言', '右上角头像 → 语言，选中文或英文'],
  ['搜索功能', '顶栏点搜索框（或按 ⌘K），输入功能名直接跳'],
  ['打印单据', '打开单据 → 顶部「打印」→ 选打印格式'],
];

// ===== 常见问题 FAQ =====
const FAQ = [
  ['登录后为什么只看到部分模块？', '这是权限控制。你被分配了哪些角色，就只能看哪些模块。需要更多功能找管理员给你加角色即可。'],
  ['地址栏为什么是英文 index？', '这是正常的设计，地址用英文更稳定，界面上显示的还是中文「首页」。'],
  ['传统产品（办公用品）要填海关编码吗？', '不用。海关编码是外贸商品才需要的，而且它是单独维护的，不强制挂在产品上。普通产品填编码、名称、商品组、单位 4 项就能保存。'],
  ['销售开单后库存怎么没变？', '库存要等「交货单提交」才扣减；采购要等「采购入库提交」才增加。只保存不提交不会动库存。'],
  ['怎么知道自己该做什么？', '看首页「待办」，或在对应模块顶部流程条里找当前环节。'],
  ['数据不小心删了/改错了怎么办？', '每天凌晨 3 点自动备份。让管理员在「数据备份」里下载最近的备份文件，用 bench restore 恢复。'],
  ['客户长期没人跟进会怎样？', '超过设定天数未跟进的客户会自动回「公海」，其他销售可以认领，避免客户浪费。'],
  ['怎么让客户走我们的业务流程？', '管理员在「流程配置」里把对应模块的步骤按你的流程排好，所有用户进该模块就能看到这条指引。'],
  ['收付款金额和发票对不上？', '看收款单/付款单是否关联了正确的发票。报表中心「订单利润」和「收付款统计」能核对。'],
];

const HELP_PAGE = function (wrapper) {
  const moduleNames = Object.keys(MODULES);
  const el = document.createElement('div');
  el.className = 'help-center-wrap';
  el.innerHTML = `
    <div class="hc-layout">
      <div class="hc-nav">
        <div class="hc-nav-group">快速上手</div>
        <div class="hc-nav-item active" data-view="starter">新手入门</div>
        <div class="hc-nav-group">功能模块</div>
        ${moduleNames.map(m => `<div class="hc-nav-item" data-view="mod" data-mod="${m}">${m}</div>`).join('')}
        <div class="hc-nav-group">速查与答疑</div>
        <div class="hc-nav-item" data-view="quick">常用操作速查</div>
        <div class="hc-nav-item" data-view="faq">常见问题</div>
      </div>
      <div class="hc-content">
        <div class="hc-title"></div>
        <div class="hc-desc"></div>
        <div class="hc-body"></div>
      </div>
    </div>
  `;
  wrapper.append(el);
  const titleEl = el.querySelector('.hc-title');
  const descEl = el.querySelector('.hc-desc');
  const bodyEl = el.querySelector('.hc-body');

  function stepHtml(items) {
    return items.map((s, i) => `
      <div class="hc-step">
        <div class="hc-step-no">${i + 1}</div>
        <div class="hc-step-body">
          <div class="hc-step-t">${s[0] || s.t || ''}</div>
          <div class="hc-step-d">${s[1] || s.d || ''}</div>
        </div>
      </div>`).join('');
  }
  function render(view, mod) {
    if (view === 'starter') {
      titleEl.textContent = '新手入门';
      descEl.textContent = '3 步快速上手，先会用再深入。';
      bodyEl.innerHTML = stepHtml(STARTER);
    } else if (view === 'quick') {
      titleEl.textContent = '常用操作速查';
      descEl.textContent = '高频操作一句话搞定。';
      bodyEl.innerHTML = QUICK.map(q => `
        <div class="hc-qitem"><div class="hc-qt">${q[0]}</div><div class="hc-qd">${q[1]}</div></div>`).join('');
    } else if (view === 'faq') {
      titleEl.textContent = '常见问题';
      descEl.textContent = '用户最常问的问题。';
      bodyEl.innerHTML = FAQ.map(q => `
        <div class="hc-faq"><div class="hc-fq">问：${q[0]}</div><div class="hc-ad">答：${q[1]}</div></div>`).join('');
    } else {
      const d = MODULES[mod];
      titleEl.textContent = mod;
      descEl.textContent = d.desc;
      bodyEl.innerHTML = stepHtml(d.steps);
    }
  }
  render('starter');
  el.querySelectorAll('.hc-nav-item').forEach(item => {
    item.addEventListener('click', () => {
      el.querySelectorAll('.hc-nav-item').forEach(x => x.classList.remove('active'));
      item.classList.add('active');
      render(item.dataset.view, item.dataset.mod);
      bodyEl.scrollTop = 0;
    });
  });
};

const hs = document.createElement('style');
hs.textContent = `
.help-center-wrap{height:100%;}
.hc-layout{display:flex;height:calc(100vh - 80px);}
.hc-nav{width:210px;flex-shrink:0;border-right:1px solid #eee;padding:12px 0;overflow-y:auto;}
.hc-nav-group{padding:10px 18px 4px;font-size:12px;font-weight:700;color:#999;letter-spacing:1px;}
.hc-nav-item{padding:9px 18px;font-size:14px;color:#444;cursor:pointer;border-left:3px solid transparent;}
.hc-nav-item:hover{background:#f5f5f5;}
.hc-nav-item.active{background:#eef5fb;border-left-color:#2980b9;color:#2980b9;font-weight:600;}
.hc-content{flex:1;padding:24px 36px;overflow-y:auto;}
.hc-title{font-size:22px;font-weight:600;color:#222;margin-bottom:6px;}
.hc-desc{font-size:14px;color:#888;margin-bottom:22px;}
.hc-step{display:flex;gap:14px;margin-bottom:16px;align-items:flex-start;}
.hc-step-no{width:28px;height:28px;flex-shrink:0;border-radius:50%;background:#2980b9;color:#fff;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:600;}
.hc-step-body{background:#fafafa;border:1px solid #eee;border-radius:8px;padding:12px 16px;flex:1;}
.hc-step-t{font-size:15px;font-weight:600;color:#333;margin-bottom:4px;}
.hc-step-d{font-size:13.5px;color:#666;line-height:1.7;}
.hc-qitem{background:#f5f8fb;border:1px solid #e3ecf3;border-radius:8px;padding:12px 16px;margin-bottom:10px;}
.hc-qt{font-size:14.5px;font-weight:600;color:#2c5d8a;margin-bottom:3px;}
.hc-qd{font-size:13.5px;color:#555;line-height:1.6;}
.hc-faq{margin-bottom:14px;padding:12px 16px;background:#fffdf5;border:1px solid #f0e8d0;border-radius:8px;}
.hc-fq{font-size:14.5px;font-weight:600;color:#8a6d1f;margin-bottom:4px;}
.hc-ad{font-size:13.5px;color:#555;line-height:1.7;}
`;
document.head.appendChild(hs);

frappe.pages['help-center'].on_page_load = function (wrapper) {
  HELP_PAGE(wrapper);
};
