# -*- coding: utf-8 -*-
"""站点业务初始化（幂等）：装 ERPNext 基础主数据 + 建公司/财年/仓库。
由 setup_bench.sh 在 install-app 后调用；手动补跑：
  cd bench && ./env/bin/python ../scripts/init_site_data.py <site>
不填参数默认取 sites/ 下唯一站点。
"""
import os
import sys


def main():
    bench_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "bench"))
    sites_dir = os.path.join(bench_root, "sites")
    if len(sys.argv) > 1:
        site = sys.argv[1]
    else:
        dirs = [d for d in os.listdir(sites_dir) if os.path.isfile(os.path.join(sites_dir, d, "site_config.json"))]
        if len(dirs) != 1:
            print(f"无法确定站点（找到 {dirs}），请传参: init_site_data.py <site>")
            sys.exit(1)
        site = dirs[0]
    os.chdir(sites_dir)
    sys.path.insert(0, sites_dir)
    import frappe
    frappe.init(site=site)
    frappe.connect()
    frappe.set_user("Administrator")

    # 1) ERPNext 基础主数据（UOM/行业/客户组/供应商组/商品组/销售阶段/职务等）
    from erpnext.setup.setup_wizard.operations import install_fixtures as fixtures
    fixtures.install("China")

    # 2) 公司（不存在才建）+ 确保默认公司被设置（解耦，幂等）
    company = "外贸演示公司"
    if not frappe.db.exists("Company", company):
        if not frappe.db.exists("Warehouse Type", "Transit"):
            for wt in ("Transit", "Inventory", "Dispatch", "Customer", "Supplier", "Production"):
                frappe.new_doc("Warehouse Type").insert(ignore_permissions=True)
        co = frappe.new_doc("Company")
        co.update({"company_name": company, "company_abbr": "WMSY",
                   "default_currency": "CNY", "country": "China"})
        co.insert(ignore_permissions=True)
    if not frappe.db.get_single_value("Global Defaults", "default_company"):
        gd = frappe.get_doc("Global Defaults")
        gd.default_company = company
        gd.save(ignore_permissions=True)

    # 3) 财年（当年，不存在才建）
    import datetime
    year = str(datetime.date.today().year)
    if not frappe.db.exists("Fiscal Year", year):
        fy = frappe.new_doc("Fiscal Year")
        fy.update({"year": year, "abbrev": year,
                   "year_start_date": f"{year}-01-01", "year_end_date": f"{year}-12-31"})
        for c in frappe.get_all("Company", fields=["name"]):
            fy.append("companies", {"company": c["name"]})
        fy.insert(ignore_permissions=True)

    # 4) 语言/地区默认（否则界面英文）
    ss = frappe.get_doc("System Settings")
    if not ss.language:
        ss.update({"language": "zh", "country": "China",
                   "time_zone": "Asia/Shanghai", "currency": "CNY"})
        ss.save(ignore_permissions=True)
    admin = frappe.get_doc("User", "Administrator")
    if not admin.language:
        admin.language = "zh"
    if not admin.default_app:
        admin.default_app = "erpnext"
    if not admin.default_workspace:
        admin.default_workspace = "外贸工作台"
    admin.save(ignore_permissions=True)

    # 5) 标记 setup wizard 完成（否则每次登录被拉进 /desk/setup-wizard）
    #    必须覆盖【所有】已安装 app：general_erp=0 时 is_setup_complete() 间歇为 false，
    #    web 多 worker 各自缓存 boot.setup_complete，/desk 与 setup-wizard 互相跳转
    #    造成主页"狂闪"（2026-08-28 线上根因，T-flash 修复）
    for _app in frappe.get_installed_apps():
        frappe.db.set_value("Installed Application", {"app_name": _app}, "is_setup_complete", 1)
    frappe.db.set_single_value("System Settings", "setup_complete", 1)
    # 6) 修正残留的 desktop:home_page 默认值（狂闪第二根因，2026-08-29 T-home-flash）：
    #    frappe 装站时把 desktop:home_page 设为 "setup-wizard"，只有 wizard 正式跑完才切走。
    #    本站走脚本式 setup，wizard 从未跑完，导致 /desk 加载后 SPA 直接实例化 setup-wizard 页，
    #    其 on_page_load 又整页跳回 /desk —— 死循环（与 is_setup_complete 无关的独立根因）。
    if frappe.db.get_default("desktop:home_page") == "setup-wizard":
        frappe.db.set_default("desktop:home_page", "workspace")

    frappe.db.commit()
    print("站点业务初始化完成:", frappe.db.get_single_value("Global Defaults", "default_company"))
    frappe.destroy()


if __name__ == "__main__":
    main()
