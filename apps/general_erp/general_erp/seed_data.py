# -*- coding: utf-8 -*-
# 一期基础数据初始化（幂等：按唯一键 upsert，可重复执行）
import frappe

PORTS = [
    ("CNSHA", "上海", "Shanghai", "中国", ""),
    ("CNXMI", "深圳盐田", "Shenzhen Yantian", "中国", ""),
    ("CNNGB", "宁波", "Ningbo", "中国", ""),
    ("CNTAO", "青岛", "Qingdao", "中国", ""),
    ("CNDLC", "大连", "Dalian", "中国", ""),
    ("CNXMN", "厦门", "Xiamen", "中国", ""),
    ("CNSZX", "广州南沙", "Guangzhou Nansha", "中国", ""),
    ("CNTXG", "天津", "Tianjin", "中国", ""),
    ("HKHKG", "香港", "Hong Kong", "中国香港", ""),
    ("SGSIN", "新加坡", "Singapore", "新加坡", ""),
    ("KRPUS", "釜山", "Busan", "韩国", ""),
    ("JPTYO", "东京", "Tokyo", "日本", ""),
    ("DEHAM", "汉堡", "Hamburg", "德国", ""),
    ("NLRTM", "鹿特丹", "Rotterdam", "荷兰", ""),
    ("USNYC", "纽约", "New York", "美国", ""),
    ("AEJEA", "杰贝阿里", "Jebel Ali", "阿联酋", ""),
    ("USLAX", "洛杉矶", "Los Angeles", "美国", ""),
]

INCOTERMS = [
    ("EXW", "工厂交货", "Ex Works", "买方承担提货后全部费用与风险"),
    ("FCA", "货交承运人", "Free Carrier", "卖方在指定地点交货给承运人"),
    ("FAS", "装运港船边交货", "Free Alongside Ship", "卖方将货物置于是船边"),
    ("FOB", "装运港船上交货", "Free On Board", "货物越过船舷后风险转移买方"),
    ("CFR", "成本加运费", "Cost and Freight", "卖方付至目的港运费，风险装运港转移"),
    ("CIF", "成本、保险费加运费", "Cost, Insurance and Freight", "卖方付运费及保险至目的港"),
    ("CPT", "运费付至", "Carriage Paid To", "卖方付至指定目的地运费"),
    ("CIP", "运费、保险费付至", "Carriage and Insurance Paid To", "卖方付运费及保险至目的地"),
    ("DAP", "目的地交货", "Delivered At Place", "卖方承担运至目的地全部费用，风险目的地转移"),
    ("DPU", "目的地卸货后交货", "Delivered at Place Unloaded", "卖方负责卸货后在目的地交货"),
    ("DAT", "运输终端交货", "Delivered at Terminal", "卖方在目的地运输终端交货（Incoterms 2010）"),
]

HS_CODES = [
    ("8471300000", "笔记本电脑", "Laptop Computer", "品牌类型|出口享惠情况|加工方法|品牌|型号|用途", "0"),
    ("8517130000", "智能手机", "Smart Phone", "品牌类型|出口享惠情况|品牌|型号|用途", "0"),
    ("9503000000", "玩具", "Toys", "品牌类型|出口享惠情况|品牌|GTIN|CAS", "0"),
    ("6109100011", "棉制T恤", "Cotton T-shirt", "品牌类型|出口享惠情况|织造方法|品牌|成分含量", "0"),
    ("3926909090", "其他塑料制制品", "Other Plastic Articles", "品牌类型|出口享惠情况|GTIN|CAS|成分含量", "0"),
]

SYSTEM_PARAMETERS = [
    ("public_pool_reclaim_days", "30", "公海线索回收天数：分配后 N 天无跟进自动回公海"),
    ("follow_up_remind_days", "3", "跟进提醒提前天数"),
    ("email_fetch_interval_minutes", "5", "邮件拉取间隔（分钟）"),
    ("quotation_valid_days", "30", "报价单默认有效期（天）"),
    ("filing_enabled", "0", "出口备案开关：1 开启 0 关闭"),
]


def _upsert(doctype, key_field, key_value, fields):
    name = frappe.db.get_value(doctype, {key_field: key_value}, "name")
    if name:
        doc = frappe.get_doc(doctype, name)
        for k, v in fields.items():
            if doc.get(k) != v:
                doc.set(k, v)
        doc.save(ignore_permissions=True)
    else:
        doc = frappe.get_doc({"doctype": doctype, key_field: key_value, **fields})
        doc.insert(ignore_permissions=True)


def seed_base_data():
    for code, port_name, english_name, country, remarks in PORTS:
        _upsert("Port", "code", code, {
            "port_name": port_name, "english_name": english_name,
            "country": country, "remarks": remarks,
        })
    for code, chinese_name, english_name, description in INCOTERMS:
        _upsert("Incoterms", "code", code, {
            "chinese_name": chinese_name, "english_name": english_name,
            "description": description,
        })
    for hs_code, product_name, english_name, declaration_elements, tax_rate in HS_CODES:
        _upsert("HS Code", "hs_code", hs_code, {
            "product_name": product_name, "english_name": english_name,
            "declaration_elements": declaration_elements, "tax_rate": tax_rate,
        })
    for param_key, param_value, description in SYSTEM_PARAMETERS:
        _upsert("System Parameter", "param_key", param_key, {
            "param_value": param_value, "description": description,
        })
    frappe.db.commit()


DEMO_CUSTOMER_EMAILS = [
    ("深圳星辰科技有限公司", "sales@shenzhenxingchen.com"),
    ("上海远航贸易有限公司", "info@shanghaiyuanhang.com"),
    ("汉堡机械设备 GmbH", "einkauf@hamburg-maschinen.de"),
    ("Tokyo Electronics Co", "purchase@tokyo-electronics.jp"),
    ("Dubai Global Import FZ", "procurement@dubai-global.ae"),
    ("New York Trading LLC", "ap@nytrading.com"),
]

DEMO_SERVICE_PROVIDERS = [
    ("DHL 国际快递", "船公司"),
    ("顺丰国际", "船公司"),
    ("COSCO 中远海运", "货代"),
    ("Maersk 马士基", "船公司"),
]

DEMO_SUPPLIERS = ["东莞电子配件厂", "宁波五金制品公司"]

DEMO_ANNOUNCEMENTS = [
    ("系统上线通知", "外贸 ERP 系统已完成部署，请使用统一门户登录。如遇问题请联系管理员。"),
    ("9 月出货高峰预警", "9 月为出货高峰，请销售与物流提前确认船期与订舱，避免出运延误。"),
]

DEMO_EMPLOYEES = [
    ("张伟", "Male", "sales1@demo.com"),
    ("李娜", "Female", "purchase1@demo.com"),
    ("王芳", "Female", "accounts1@demo.com"),
]


def seed_demo_data():
    """演示种子数据（幂等）：服务商/供应商/公告/客户邮箱/群发示例/员工。

    每项独立 try/commit，单条失败不阻断其余；员工依赖 Gender 主数据，
    Gender 缺失时先建 Male/Female 再建员工，仍失败仅跳过员工不影响其他项。
    """
    # 1) 客户补邮箱
    for cname, email in DEMO_CUSTOMER_EMAILS:
        try:
            if frappe.db.exists("Customer", cname) and not frappe.db.get_value("Customer", cname, "email_id"):
                frappe.db.set_value("Customer", cname, "email_id", email)
            frappe.db.commit()
        except Exception as e:
            frappe.db.rollback()
            frappe.log_error(f"demo seed customer email {cname}: {e}", "seed_demo_data")

    # 2) 服务商
    try:
        for name, ptype in DEMO_SERVICE_PROVIDERS:
            if not frappe.db.exists("Service Provider", {"provider_name": name}):
                d = frappe.new_doc("Service Provider")
                d.update({"provider_name": name, "provider_type": ptype})
                d.insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error("demo seed service providers: " + str(e), "seed_demo_data")

    # 3) 供应商
    try:
        for name in DEMO_SUPPLIERS:
            if not frappe.db.exists("Supplier", name):
                d = frappe.new_doc("Supplier")
                d.update({"supplier_name": name, "supplier_group": "Local",
                          "territory": "China", "default_currency": "CNY"})
                d.insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error("demo seed suppliers: " + str(e), "seed_demo_data")

    # 4) 公告
    try:
        for title, content in DEMO_ANNOUNCEMENTS:
            if not frappe.db.exists("Announcement", {"title": title}):
                a = frappe.new_doc("Announcement")
                a.update({"title": title, "content": content, "is_pinned": 0})
                a.insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error("demo seed announcements: " + str(e), "seed_demo_data")

    # 5) 群发示例（带收件人 + 打开/点击数，供"群发效果"报表演示）
    try:
        if not frappe.db.exists("Bulk Email", {"subject": "新品目录推送"}):
            b = frappe.new_doc("Bulk Email")
            b.update({"subject": "新品目录推送",
                      "message_body": "<p>各位客户好，本季新品目录已更新，请查收附件。</p>",
                      "send_status": "已发送",
                      "sent_at": "2026-08-25 10:00:00"})
            custs = frappe.get_all("Customer", fields=["name", "customer_name", "email_id"],
                                   filters={"email_id": ["like", "%@%"]})[:3]
            for c in custs:
                b.append("customers", {"customer": c["name"],
                                        "customer_name": c["customer_name"],
                                        "email_id": c["email_id"]})
            b.insert(ignore_permissions=True)
            b.total_count = len(custs)
            b.success_count = len(custs)
            b.fail_count = 0
            b.opened_count = max(1, len(custs) - 1)
            b.clicked_count = 1
            b.save(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error("demo seed bulk email: " + str(e), "seed_demo_data")

    # 6) 员工（依赖 Gender / Designation 主数据；缺失先建）
    try:
        for g in ("Male", "Female"):
            if not frappe.db.exists("Gender", g):
                gd = frappe.new_doc("Gender")
                gd.gender = g
                gd.insert(ignore_permissions=True)
        for desig in ("销售专员", "采购专员", "财务专员"):
            if not frappe.db.exists("Designation", desig):
                dd = frappe.new_doc("Designation")
                dd.designation_name = desig
                dd.insert(ignore_permissions=True)
        frappe.db.commit()
        dept_map = {"sales1@demo.com": ("Sales - 外", "销售专员"),
                    "purchase1@demo.com": ("Purchase - 外", "采购专员"),
                    "accounts1@demo.com": ("Accounts - 外", "财务专员")}
        companies = frappe.get_all("Company", pluck="name")
        company = companies[0] if companies else None
        for first, gender, user in DEMO_EMPLOYEES:
            if not frappe.db.exists("Employee", {"user_id": user}):
                dept, desig = dept_map[user]
                e = frappe.new_doc("Employee")
                e.update({"first_name": first, "gender": gender,
                          "date_of_birth": "1990-05-01", "date_of_joining": "2024-03-01",
                          "status": "Active", "company": company,
                          "department": dept, "designation": desig, "user_id": user})
                e.insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error("demo seed employees: " + str(e), "seed_demo_data")

    frappe.clear_cache()



def after_install():
    if frappe.db.exists("DocType", "Port"):
        seed_base_data()
    if frappe.db.exists("DocType", "Service Provider"):
        seed_demo_data()
