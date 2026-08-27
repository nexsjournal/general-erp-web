# general-erp-web

基于 **ERPNext**（Frappe Framework）二次开发的通用 ERP 项目。

- 基座：frappe `version-16` + erpnext `version-16`（固定分支，升级走专门流程，见下文）
- 自定义功能：`apps/general_erp/`（唯一允许写代码的地方）
## 文档

- [首次访问指南：登录页与初始配置](docs/first-run-guide.md)
- [设计系统规范](docs/design-system/README.md)（色彩/字体/图标/组件/表单/交互/动效/图表）
- [开源 ERP 调研报告](docs/open-source-erp-research.md)
- [外贸 ERP 功能需求规格说明书](docs/feature-requirements.md)（基于客户功能清单整理，含红字 P0 重点与实施路线）

## 已实现功能（对照 [功能需求规格](docs/feature-requirements.md)，P0/P1/P2 全量落地）

- **外贸销售主链路**：线索（网站留言自动入线索、分发留痕）→ 客户（我的客户/公海回收/热点/移交）→ 客户跟进（电话/邮件/拜访，公海回收依据）→ 客户 360 全景（共享/合并）→ 商机 → 报价单 → 销售订单 → 出运明细单（港口/贸易术语）→ 外贸单证 → 收款 → 订单利润
- **营销**：营销活动、邮件群发（模板变量 + 发送统计 + 频率限制校验）、邮件模板、网站留言 Web Form（`/website-lead` + 官网嵌入代码页）
- **采购与库存**：供应商、采购订单（审批工作流：草稿→待审批→已审批/已驳回）、采购入库、来料验货单、物料（HS 编码）、入库/库存余额/出库
- **OA**：待办（ToDo）、公告、文件管理、工作检查（自检 + ToDo 提醒）、工作日历（节假日/跟进/出运）
- **邮件**：邮件中心（待处理/收件箱/草稿箱/已发送/待审批/已删除）、邮件增强（自动审批规则、审批通过、分发、建档到客户、归档、CSV 导出、下属邮件）、IMAP 邮箱账号接入、营销账号频率限制（日发送上限/单收件人上限）、发送跟踪（打开像素 + 点击跳转）
- **基础平台**：港口、贸易术语、HS 编码、系统参数、币种汇率（今日汇率数字卡）、服务商、邮箱账号、统计设置（公海天数 + 报表订阅定时推送 + 报表可见角色）、区域设置（语言/时区/日期）
- **报表（18 个）**：外销/出运/订单利润/产品/采购/收款/付款/费用/客户统计/线索/商机/邮件统计、库存预警、员工业绩排行、员工工作情况表、客户分析、感兴趣分析、报价分析
- **工作台与演示**：外贸工作台（15 模块卡片 + 12 快捷方式 + 5 数字卡 + 图表）、商机批复（待批复/已批复/待回复三态 + 留痕 + 列表筛选视图）、业务流程页（按功能清单串联全部单据，可点击跳转）、侧边栏 37 项、用户参数入口（User 偏好设置）
- **多语言**：中文默认 + 英文翻译（zh.csv / en.csv，567 条词条）

## 目录结构

```
general-erp-web/
├── apps/general_erp/       # ★ 自定义 app（git 管理，所有新功能在这里）
├── bench/                  # Frappe Bench（生成物，大部分不入库；apps/general_erp 是软链）
├── scripts/
│   ├── setup_bench.sh      # 一键初始化（新机器跑一次）
│   └── start_dev.sh        # 启动本地开发服务（端口见 bench/sites/common_site_config.json）
└── docs/                   # 调研与开发文档
```

## 快速开始（新 Mac，需已装 Homebrew）

```bash
./scripts/setup_bench.sh    # 首次约 15-30 分钟（装依赖 + 下载基座 + 建站点 + 编译）
./scripts/start_dev.sh      # 启动服务（前台运行，Ctrl+C 停止）
# 浏览器打开 http://localhost:8005，登录 **Administrator / admin123**
# 说明：frappe 登录框标注「邮件」，实际按用户名匹配（普通用户用户名即邮箱）；
# 已开启 allow_login_using_user_name 并把 Administrator 的 username 设为邮箱，两种写法均可
```

换电脑/复制代码后：复制整个项目目录 → 跑 `./scripts/setup_bench.sh`（venv 和站点数据库会自动重建）。

## 端口与服务

| 端口 | 服务 | 说明 |
|---|---|---|
| 8002 | ERPNext Web | 主入口 |
| 9002 | Socket.IO | 实时通信（勿动） |
| 11000-13000 | Redis 队列 | bench 自管理的 redis 实例 |
| 6379 | Redis（系统） | brew services |
| 3307 | MariaDB（ERP 专用） | LaunchAgent `homebrew.mxcl.mariadb-erp` 开机自启；**与 3306 上的 MySQL 实例互不干扰** |

> 注意：`/opt/homebrew/etc/my.cnf` 里 MySQL 9 的 `mysqlx-*` 参数对 MariaDB 不兼容，
> ERP 实例专用配置在 `/opt/homebrew/etc/mariadb-erp.cnf`，数据目录 `/opt/homebrew/var/mariadb`。

## 添加功能（口子）

所有新功能只写进 `apps/general_erp/`：

```bash
cd bench
# 1) 新建自定义单据
bench --site general.erp.local new-doctype "示例单据" --module "General ERP"
# 2) 结构变更后同步数据库
bench --site general.erp.local migrate
# 3) 重启/热加载（start_dev.sh 的 watch 会自动 reload，一般不用手动）
```

- 扩展 ERPNext 官方单据行为：在 `apps/general_erp/general_erp/hooks.py` 用 `doc_events` 钩子，**不修改官方源码**。
- 定时任务、fixtures、全局 JS/CSS：都在 `hooks.py` 有注释示例。
- 完整约定见 `apps/general_erp/README.md`。

## 常用命令

```bash
cd bench
bench --site general.erp.local console          # python 调试台
bench --site general.erp.local run-tests --app general_erp   # 跑自定义 app 测试
bench --site general.erp.local set-config lang zh           # 切换界面语言
bench --site general.erp.local reset-permissions --force    # 重置权限
```

## 升级基座

- **小版本（16.x 内）**：`bench update --patch`（自定义 app 无需改动时较安全）。
- **大版本（如 17）**：单独开分支，`bench --site x reinstall` 或重建站点；先把 `apps/general_erp` 在新版本上回归一遍再合入。
- 升级后固定新的 `FRAPPE_BRANCH`/`ERPNEXT_BRANCH` 写入 `scripts/setup_bench.sh` 顶部并同步文档。

## 多人协作

- 入库内容：`apps/general_erp/`、`scripts/`、`README.md`、`docs/`（bench 生成物已 gitignore）。
- 每人本地独立站点数据库（`bench new-site` 建各自的 site 即可，互不干扰）。
- 数据库账号、密码在 `scripts/setup_bench.sh` 顶部集中配置。
