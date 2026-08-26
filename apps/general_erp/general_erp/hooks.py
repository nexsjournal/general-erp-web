# -*- coding: utf-8 -*-
# ============================================================
# general_erp —— 自定义功能挂载点
# 所有新增业务都写在本 app（apps/general_erp）里，
# 不要修改 apps/frappe 与 apps/erpnext 的源码。
# ============================================================

app_name = "general_erp"
app_title = "General ERP"
app_publisher = "general-erp-web"
app_description = "general-erp-web 自定义 ERP 功能"
app_email = "dev@local"
app_license = "GPL-3.0"

# 依赖的其他 app（如 ["erpnext"]）
required_apps = []

# 自定义 app 的全局 CSS/JS（会被注入到每个页面）
app_include_css = ["erp_theme.bundle.css"]
app_include_js = ""

# 数据库 fixtures（预置数据，migrate 时自动同步）
# fixtures = []

# 定时任务（scheduler）
# scheduler_events = {
#     "general_erp": {
#         "cron": {
#             "*/10 * * * *": ["general_erp.general_erp.doctype.demo_note.demo_note.run_scheduled"],
#         }
#     }
# }

# 监听官方 DocType 事件（扩展 ERPNext 单据行为的标准方式，不改官方代码）
# doc_events = {
#     "Sales Invoice": {
#         "on_submit": "general_erp.general_erp.doctype.demo_note.demo_note.on_sales_invoice_submit",
#     }
# }

# 工作台入口（在 Desk 首页展示自定义页面，可选）
# workspace_items = ...
