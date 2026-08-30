# 变更历史（CHANGELOG）

格式：日期倒序，每轮交付一节，含功能 / 修复 / 测试结论 / 提交号。

## 2026-08-30（v1.2，会话/首页体验 + 第二轮 graph 复测）

### 修复（用户报修项）
- **会话超时机制**：闲置超 8 小时强制重新输账号密码。根因=frappe 默认 session_expiry=170:00（≈7 天），客户反馈过段时间再登录不用输密码。现 System Settings.session_expiry=8:00，site_setup.sync_user_login_settings 幂等固化（after_migrate 兜底防回滚）。`7d6d817` `94585d9`
  - 说明：`7d6d817` 误提交到顶层 stray 副本 apps/general_erp/general_erp/site_setup.py（未被 hooks import），`94585d9` 将固化落到实际加载的 general_erp.general_erp.site_setup（嵌套）。DB 值已在线验证 8:00。
- **登录后首页落地验证**：干净会话实测裸 IP → 登录页 → 登录后落 /desk/index（金蝶式首页）；所有系统用户 default_workspace=index，普通用户侧栏不显示 ERP工作台。用户此前看到的 12 格磁贴墙（frappe 内置 Home 工作区）为浏览器旧会话残留，非功能缺失。

### 补记（PR#2 已合入但文档漏记）
- **审批流程自助设置向导**：组织管理→审批设置（流程清单/待我审批/三问式向导）；API api_approval_wizard.py 生成标准 frappe Workflow；最多 3 级审批（审批1/2/3 独立状态）；小额免批（金额阈值 condition 开关）；超时催办（daily scheduler + redis 去重）；approval_guard 中间态判定改 DB 状态（修 v16 apply_workflow 合法首提交被误拦）。`572fd6e` `916c6e5`

### 测试与质量
- **graph 第二轮全量复测**（4 路并行 + 独立验证）：功能 A 14/14 模块可达无空白页 + 销售订单深层链走通返回不丢态；数据 B 30+ 单据接口全 200 有数 + 10 并发 P95=586ms（<2s 达标）；安全 C 越权矩阵正确（sales1 用户列表只见自己、财务/采购/跨角色单据 403、admin 全量）；UI D ERP工作台对业务员正确隐藏、死按钮/图标探针误报复测无实锤。**0 P0 / 0 P1**。报告 docs/reports/graph测试报告-2026-08-30.md（第二轮节）。`91a640f`
- **回归基线升级 33→44 项**：chain 2/2 + fin_reports 4/4 + modules 15/15 + permissions 12/12 + approval_guard 7/7 = 44/44 PASS。
- **环境项（非代码缺陷）**：本地 bench serve(werkzeug) 不带 socket.io 代理，/socket.io 轮询 404（正式 bench start/gunicorn 部署才有）；影响实时通知实时性，核心 CRUD/报表/审批全走 HTTP 不受影响。

## 2026-08-30（v1.1）

### 用户与权限
- **用户隐私权限收紧**（用户拍板）：普通用户「用户管理」列表只看到自己；改自己的资料/密码不受影响；读他人资料 403。`1861152`
  - 机制：Custom DocPerm 收回 Desk User 对 User 单据的 read/select；新建「流程设计」角色（User read+select、Workflow/Module Flow 读写）授予 boss1、salesm1；超管 System Manager 原生全权不受影响。
  - site_setup.sync_user_privacy 幂等固化（migrate 防回滚，存在则更新防重复 CDP）。
- **7 岗位角色体系**：销售/外贸专员/采购/库存/财务/总经理/系统管理员，选岗位自动带整套原生角色，默认权限矩阵不变。`7cecf1a`
- **无邮箱建号**：邮箱非必填，用户名即登录名，用户表单可生成用户名/密码。`0796fc4`

### 界面与导航
- **金蝶式首页**：登录后直达「首页」（今日概览数字卡 + 12 业务模块入口），/index 短路径直达。`18b99c9`
- **两级导航**：左侧功能域 + 右侧子功能磁贴；侧边栏 14 项业务顺序固定。`199d6ae`
- **品牌统一「太康生物ERP」**（技术模块名 General ERP 保持不变防导入失败）。`2a724e0`
- **帮助中心**：侧栏入口，快速上手 3 步 + 13 模块分步教程 + 10 常用操作速查 + 9 FAQ。`71e2bdd` `3a95a6b`
- **轻量流程配置**：Module Flow DocType，每个模块页顶部渲染可后台编辑的流程步骤条，改完即时生效。`8a0bd4b`
- **狂闪除根**：setup-wizard 死循环根治（清脏 session_last_route + set_route 守卫）。`73aabf3` `6240f98` `4651f0e` `b237d23`
- **金额口径**：CNY 显示「数字 + 元」，数字卡全额不缩写，图表坐标轴千分位，今日汇率 2 位小数。`a2545a9` `084d4bd`

### 数据与备份
- **每日自动备份**：scripts/backup_daily.sh（DB dump + 私有文件 + 站点配置，保留 14 天）+ launchd 每日 03:00；已做恢复演练（762 表可还原）。`c34f317`
- **数据与备份页**：系统设置内备份列表 / 一键备份 / 下载（仅 System Manager）。`fda71ee`

### 修复（graph 全角度测试驱动）
- **外销统计 N+1**：相关子查询改 LEFT JOIN 预聚合，口径守恒验证通过。`084d4bd`
- **今日汇率 9 位小数**：强制 2 位小数（非侵入 bundle 补丁）。`084d4bd`
- **回归脚本跨天误报**：TODAY 由硬编码改动态取当天。`084d4bd`
- **批次统计出数**：真实单据链路（Batch + Stock Entry），不手插 SLE。`bf7221f`
- **SVG 告警消音**：Chart.js 空串颜色告警（P2 非侵入）。`bf7221f`
- **原生财务报表自动出数**：三张表预填当前会计年度，点开即有数。`39c3545`

### 测试与质量
- **graph 全角度测试**（4 路并行：功能/数据/安全/UI + 独立验证）：83 页 0 真实问题、回归 33/33、越权矩阵 0 放行、注入 7/7 安全、无 P0。报告见 docs/reports/graph测试报告-2026-08-30.md。
- **全量 E2E**：83 页 + 25 报表 + 33 回归，无 P0/P1。`7ab58bb`
- **回归固化**：tests/regression/ 33 项 + scripts/regression.sh 一键入口（环境自愈前置，测试数据自动清理）。`39c3545`

### 遗留（不阻断交付，见 docs/reports/T13-待办-graph测试遗留-P2.md）
- D2：生产部署用 WSGI（gunicorn/nginx）替代 frappe serve，避免 500 响应带堆栈/绝对路径。
- D3：登录锁定默认已生效（实测 10 连败锁 60s）；注意锁定按来源 IP，生产多人同 NAT 出口时建议确认粒度。
- D4：付款单并发双击败方收 500 死锁报错（数据安全，仅报错不友好）——体验优化。

## 2026-08-29（v1.0）
- 外贸销售主链路、营销、采购与库存、OA、邮件中心、18 报表、工作台与演示等 P0/P1/P2 全量落地。
- 多语言中文默认 + 英文翻译（zh.csv/en.csv 567 词条）。
- 站点初始化 init_site_data.py（基础主数据/公司/财年，幂等）。`a109f7d`

> 更早的逐 commit 记录见 git log。
