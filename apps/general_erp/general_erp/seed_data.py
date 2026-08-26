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


def after_install():
    if frappe.db.exists("DocType", "Port"):
        seed_base_data()
