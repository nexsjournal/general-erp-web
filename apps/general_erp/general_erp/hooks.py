# -*- coding: utf-8 -*-
# ============================================================
# general_erp —— 自定义功能挂载点
# 所有新增业务都写在本 app（apps/general_erp）里，
# 不要修改 apps/frappe 与 apps/erpnext 的源码。
# ============================================================

app_name = "general_erp"
app_title = "太康生物ERP"
app_publisher = "general-erp-web"
app_description = "general-erp-web 自定义 ERP 功能"
app_email = "dev@local"
app_license = "GPL-3.0"

# 依赖的其他 app（如 ["erpnext"]）
required_apps = []

# 自定义 app 的全局 CSS/JS（会被注入到每个页面）
app_include_css = ["erp_theme.bundle.css"]
app_include_js = "erp_fixes.bundle.js"

# DocType 控制器覆盖（数据隔离等，不动 erpnext 源码）
override_doctype_class = {
	"Customer": "general_erp.general_erp.overwrite.customer.customer.Customer",
	# 无邮箱账号（T-user-login）：name 取 username，登录走用户名
	"User": "general_erp.general_erp.overwrite.user.user.User",
}
# 数据库 fixtures（预置数据，migrate 时自动同步）
# fixtures = []

# 定时任务（scheduler）
scheduler_events = {
    "daily": [
        # 公海自动回收：N 天无跟进的私有客户移入公海（docs/feature-requirements.md 4.4）
        "general_erp.general_erp.doctype.customer_follow_up.customer_follow_up.auto_pool_customers",
        # 工作检查提醒：检查日当天待检查任务发待办（4.1）
        "general_erp.general_erp.doctype.work_check.work_check.remind_work_checks",
        # 报表订阅推送：按频率/星期发送报表 CSV 邮件（4.11 统计设置）
        "general_erp.general_erp.doctype.statistics_settings.statistics_settings.send_report_subscriptions",
    ],
    "cron": {
        # IMAP 收件同步：每 5 分钟拉取启用邮箱的未读邮件（4.3 邮箱设置）
        "*/5 * * * *": [
            "general_erp.general_erp.mail_sync.fetch_incoming_mails",
        ]
    }
}

# 监听官方 DocType 事件（扩展 ERPNext 单据行为的标准方式，不改官方代码）
doc_events = {
    "Lead": {
        # 网站留言频控（T2-18）：同 IP 每小时最多 5 条
        "before_insert": "general_erp.general_erp.crm_utils.website_lead_rate_limit",
    }
}

# 工作台入口（在 Desk 首页展示自定义页面，可选）
# workspace_items = ...

# 基础数据初始化（安装后自动播种，幂等）
after_install = "general_erp.general_erp.site_setup.after_install"

# 每次 migrate 后同步自定义字段/Web Form（代码引用的结构随代码走，不靠手工加库）
after_migrate = "general_erp.general_erp.site_setup.after_migrate"

# Jinja 模板扩展方法（打印格式等模板中可直接调用 money_in_words_cn(金额, 币种)）
jinja = {
    "methods": ["general_erp.api.money_in_words_cn"],
}

# 登录/登出日志（安全审计，docs/feature-requirements.md 第 9 章）
on_login = "general_erp.general_erp.doctype.login_log.login_log.on_login"
on_logout = "general_erp.general_erp.doctype.login_log.login_log.on_logout"

# T-nav-fix: 已登录用户访问根地址 / 与 /desk 裸路由时直达 首页 workspace（金蝶式两级首页），
# 不影响 /desk/xxx 子路由与未登录访问（未登录仍走登录页）。
# T-nav-fix: 登录落地导航统一（金蝶式两级首页，非侵入，不动 frappe/erpnext 源码）
# 根地址 / 与 /desk 裸路由 301 到 /desk/首页；/desk/xxx 子路由不受影响；
# 未登录访问会 301 到 /desk/首页 再弹回登录页，行为与原生一致
website_redirects = [
	{"source": "", "target": "/desk/%E9%A6%96%E9%A1%B5"},
	{"source": "desk", "target": "/desk/%E9%A6%96%E9%A1%B5"},
]
