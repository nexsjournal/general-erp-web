# general-erp-web

基于 **ERPNext**（Frappe Framework）二次开发的通用 ERP 项目。

- 基座：frappe `version-16` + erpnext `version-16`（固定分支，升级走专门流程，见下文）
- 自定义功能：`apps/general_erp/`（唯一允许写代码的地方）
## 文档

- [首次访问指南：登录页与初始配置](docs/first-run-guide.md)
- [设计系统规范](docs/design-system/README.md)（色彩/字体/图标/组件/表单/交互/动效/图表）
- [开源 ERP 调研报告](docs/open-source-erp-research.md)
- [外贸 ERP 功能需求规格说明书](docs/feature-requirements.md)（基于客户功能清单整理，含红字 P0 重点与实施路线）

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
# 浏览器打开 http://localhost:8002，登录 **Administrator / admin123**（frappe 按用户名匹配，必须用 `Administrator`，邮箱 `admin@example.com` 无效）
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
