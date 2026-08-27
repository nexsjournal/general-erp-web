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

    # 4) 标记 setup wizard 完成（否则每次登录被拉进 /desk/setup-wizard）
    #    v16 的 is_setup_complete() 要求 frappe+erpnext 两个 app 的 is_setup_complete=1
    for _app in ("frappe", "erpnext"):
        frappe.db.set_value("Installed Application", {"app_name": _app}, "is_setup_complete", 1)
    frappe.db.set_single_value("System Settings", "setup_complete", 1)

    frappe.db.commit()
    print("站点业务初始化完成:", frappe.db.get_single_value("Global Defaults", "default_company"))
    frappe.destroy()


if __name__ == "__main__":
    main()
