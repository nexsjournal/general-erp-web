# general_erp（自定义功能 app）

本项目所有**新增/定制功能**都放在这个 app 里，`apps/frappe` 与 `apps/erpnext` 视为只读基座。

## 目录结构

```
general_erp/                    # app 根目录
├── pyproject.toml              # app 元信息（改 app 描述/版本在这里）
└── general_erp/
    ├── __init__.py             # 版本号
    ├── hooks.py                # ★ 挂载点：JS/CSS、定时任务、doc_events、fixtures
    ├── modules.txt             # 业务模块清单（每个模块对应一个业务域）
    ├── patches.txt             # 数据迁移补丁（版本升级时按顺序执行）
    └── general_erp/            # 默认业务模块
        └── doctype/            # ★ 自定义单据（DocType）都建在这里
```

## 常用开发命令（在 bench 根目录执行）

```bash
# 新建自定义单据（DocType）
bench --site general.erp.local new-doctype "示例单据" --module "General ERP"

# 代码变更后让数据库结构/缓存生效
bench --site general.erp.local migrate

# 调试后台（python 交互）
bench --site general.erp.local console

# 跑本 app 的测试
bench --site general.erp.local run-tests --app general_erp
```

## 规则

1. 新功能 = 新 DocType / 新页面 / hooks.py 里挂事件，**不改官方代码**。
2. 需要改 ERPNext 原有单据行为：用 `doc_events` 钩子或继承覆盖，不用 patch 官方文件。
3. 数据结构变更必须通过 DocType JSON / migrate 完成，禁止手工改表。
4. 本目录随 git 版本管理；`bench/apps/general_erp` 是指向这里的软链。
