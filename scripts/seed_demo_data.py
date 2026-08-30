# -*- coding: utf-8 -*-
"""演示数据种子（幂等）：tests/regression 依赖的演示数据统一从这里来。

背景（2026-08-30 PR#1 审核修复）：原演示数据（外贸演示公司/ITM-004/demo 用户群等）
只在开发机手工创建、从未入库，换机后回归脚本无法复现。本脚本补齐全部依赖：
公司默认/仓库/银行账户/物料+BOM/供应商/客户(含数据隔离口径)/6 个演示用户(带角色)。
用法:
  cd bench && ./env/bin/python ../scripts/seed_demo_data.py <site>
依赖: 先跑 init_site_data.py（ERPNext 基础主数据/公司/财年）+ bench migrate（app 结构）。
"""
import os
import sys

COMPANY = "外贸演示公司"
WH = "Finished Goods - 外"
ITEM = "ITM-004"
ITEM_NAME = "演示库存商品"


def connect():
    bench_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "bench"))
    sites_dir = os.path.join(bench_root, "sites")
    if len(sys.argv) > 1:
        site = sys.argv[1]
    else:
        dirs = [d for d in os.listdir(sites_dir) if os.path.isfile(os.path.join(sites_dir, d, "site_config.json"))]
        if len(dirs) != 1:
            print(f"无法确定站点（找到 {dirs}），请传参: seed_demo_data.py <site>")
            sys.exit(1)
        site = dirs[0]
    os.chdir(sites_dir)
    sys.path.insert(0, sites_dir)
    import frappe
    frappe.init(site=site)
    frappe.connect()
    frappe.set_user("Administrator")
    return frappe


def main():
    frappe = connect()

    # 0) 前置：公司/财年/仓库类型
    from general_erp.general_erp.site_setup import sync_site_setup
    sync_site_setup(with_seed=True)
    if not frappe.db.exists("Company", COMPANY):
        print("先跑 init_site_data.py（建公司/财年）")
        sys.exit(1)
    if not frappe.db.get_single_value("Global Defaults", "default_company"):
        frappe.db.set_single_value("Global Defaults", "default_company", COMPANY)

    # 1) 仓库 Finished Goods - 外（缺仓库类型先补）
    for wt in ("Inventory", "Production", "Dispatch", "Supplier", "Customer"):
        if not frappe.db.exists("Warehouse Type", wt):
            frappe.get_doc({"doctype": "Warehouse Type", "warehouse_type_name": wt,
                            "name": wt}).insert(ignore_permissions=True)
    if not frappe.db.exists("Warehouse", WH):
        w = frappe.new_doc("Warehouse")
        w.update({"warehouse_name": WH, "company": COMPANY, "warehouse_type": "Inventory"})
        w.insert(ignore_permissions=True)
    # 2) 银行账户 Cash - 外（挂在公司现有现金组下，复用中文 COA 不新建根）
    if not frappe.db.exists("Account", "Cash - 外"):
        # 找一个可用现金组（现款/现金/Cash 类的 group），没有则挂 Cash In Hand 根
        parent = None
        for cand in ("现款", "现金", "Cash In Hand", "Cash"):
            parent = frappe.db.get_value(
                "Account", {"account_name": cand, "company": COMPANY, "is_group": 1}, "name")
            if parent:
                break
        if not parent:
            parent = frappe.db.get_value(
                "Account", {"company": COMPANY, "is_group": 1, "root_type": "Asset"}, "name")
        a = frappe.new_doc("Account")
        a.update({"account_name": "Cash", "company": COMPANY, "account_type": "Cash",
                  "is_group": 0, "parent_account": parent})
        a.insert(ignore_permissions=True)

    # 3) 物料 ITM-004（库存商品）+ 原料 + BOM(item=ITM-004, is_default, company)
    if not frappe.db.exists("Item", ITEM):
        i = frappe.new_doc("Item")
        i.update({"item_code": ITEM, "item_name": ITEM_NAME, "stock_uom": "Unit",
                  "is_stock_item": 1, "item_group": "Products"})
        i.insert(ignore_permissions=True)
    if not frappe.db.exists("Item", "RAW-001"):
        i = frappe.new_doc("Item")
        i.update({"item_code": "RAW-001", "item_name": "演示原料", "stock_uom": "Unit",
                  "is_stock_item": 1, "item_group": "Raw Material"})
        i.insert(ignore_permissions=True)
    bom = frappe.db.get_value("BOM", {"item": ITEM, "is_default": 1}, "name")
    if bom and frappe.db.get_value("BOM", bom, "docstatus") == 0:
        _bd = frappe.get_doc("BOM", bom)
        _bd.submit()
    if not bom:
        bd = frappe.new_doc("BOM")
        bd.update({"item": ITEM, "item_name": ITEM_NAME, "company": COMPANY,
                   "quantity": 1, "is_default": 1, "source_warehouse": WH, "wip_warehouse": WH})
        bi = bd.append("items", {})
        bi.update({"item_code": "RAW-001", "qty": 2, "source_warehouse": WH})
        bd.insert(ignore_permissions=True)
        if bd.docstatus == 0:
            bd.submit()

    # 4) 供应商
    if not frappe.db.exists("Supplier", "深圳华强电子供应商"):
        s = frappe.new_doc("Supplier")
        s.update({"supplier_name": "深圳华强电子供应商", "territory": "China"})
        s.supplier_group = frappe.db.get_value("Supplier Group", {"name": "Local"}, "name") or \
            frappe.db.get_value("Supplier Group", {"is_group": 0, "name": ["not like", "%All%"]}, "name")
        s.insert(ignore_permissions=True)

    # 5.1) User Permission（客户数据隔离依赖：sales1 仅远航；salesm1 仅汉堡）
    for user, cust in [("sales1@demo.com", "上海远航贸易有限公司"),
                       ("salesm1@demo.com", "汉堡机械设备 GmbH")]:
        if not frappe.db.exists("User Permission", {"user": user, "allow": "Customer", "for_value": cust}):
            frappe.get_doc({"doctype": "User Permission", "user": user, "allow": "Customer",
                            "for_value": cust}).insert(ignore_permissions=True)

    # 5.2) 期初库存（销售链交货要出 10 个 ITM-004，无期初会 NegativeStockError）
    actual = frappe.db.sql("select actual_qty from `tabBin` where item_code=%s and warehouse=%s",
                          (ITEM, WH))
    if not actual or actual[0][0] < 10:
        se = frappe.new_doc("Stock Entry")
        se.update({"stock_entry_type": "Material Receipt", "purpose": "Material Receipt",
                   "company": COMPANY, "posting_date": frappe.utils.today()})
        se.append("items", {"item_code": ITEM, "qty": 100, "basic_rate": 10,
                            "t_warehouse": WH, "t_warehouse_name": WH})
        se.insert(ignore_permissions=True)
        se.submit()

    # 6) 演示用户（幂等：存在则只对齐角色）
    # 角色与审批工作流 transition 对齐（PP 提交=Stock Manager / 审批=Purchase Manager；
    # PO 提交=Sales / 审批=Sales Manager；向导 e2e 用 boss1 走审批通过）：
    USERS = [
        ("sales1@demo.com", "销售一", ("Sales User", "销售")),
        ("salesm1@demo.com", "销售经理", ("Sales Manager",)),
        ("purchase1@demo.com", "采购一", ("Purchase User", "Sales")),
        ("stock1@demo.com", "库存一", ("Stock User", "Stock Manager")),
        ("accounts1@demo.com", "财务一", ("Accounts User",)),
        ("boss1@demo.com", "总经理", ("总经理", "Sales Manager", "Purchase Manager", "Purchase User", "流程设计")),
    ]
    for email, first_name, roles in USERS:
        if frappe.db.exists("User", email):
            u = frappe.get_doc("User", email)
            u.flags.ignore_permissions = True
            for r in roles:
                if not any(x.role == r for x in u.get("roles") or []):
                    u.append("roles", {"role": r})
            u.save(ignore_permissions=True)
        else:
            u = frappe.new_doc("User")
            u.update({"email": email, "first_name": first_name, "enabled": 1,
                      "user_type": "System User", "send_welcome_email": 0,
                      "new_password": "Demo@2026"})
            for r in roles:
                u.append("roles", {"role": r})
            u.insert(ignore_permissions=True)

    # 5) 客户（数据隔离口径：远航=sales1 私有；汉堡=他人私有，非公海）
    for name, owner in [("上海远航贸易有限公司", "sales1@demo.com"), ("汉堡机械设备 GmbH", "salesm1@demo.com")]:
        if not frappe.db.exists("Customer", name):
            c = frappe.new_doc("Customer")
            c.update({"customer_name": name, "customer_type": "Company", "territory": "China",
                      "customer_group": frappe.db.get_value("Customer Group", {"is_group": 0}, "name"),
                      "sales_owner": owner})
            c.insert(ignore_permissions=True)
        else:
            cur = frappe.db.get_value("Customer", name, "sales_owner")
            if not cur:
                frappe.db.set_value("Customer", name, "sales_owner", owner)

    frappe.db.commit()

    print("演示数据就绪: 公司=%s 仓库=%s 物料=%s BOM=%s 客户=2 用户=%d"
          % (COMPANY, WH, ITEM,
             frappe.db.get_value("BOM", {"item": ITEM, "is_default": 1}, "name"), len(USERS)))


if __name__ == "__main__":
    main()
