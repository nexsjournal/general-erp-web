# -*- coding: utf-8 -*-
"""为 Mail 补 message_id 字段（UNIQUE 索引），幂等。

背景：IMAP 同步用 Message-Id 去重（mail_sync.py），schema 缺该列时 exists 恒空，
每 5 分钟重复拉全部未读邮件（P0-3）。

说明：当前 frappe 版本的 Custom Field 无 is_unique 列，唯一性用数据库
UNIQUE 索引保证（MySQL 唯一索引允许多个 NULL，不影响手工建单）。
回滚：ALTER TABLE `tabMail` DROP INDEX `message_id_uniq`; 并删 Custom Field。
"""
import frappe

def execute():
	# 1) 字段（走 frappe 正规入口，自动加列）
	if not frappe.db.exists("Custom Field", {"dt": "Mail", "fieldname": "message_id"}):
		from frappe.custom.doctype.custom_field.custom_field import create_custom_field
		create_custom_field("Mail", {
			"fieldname": "message_id",
			"label": "Message-Id",
			"fieldtype": "Data",
			"no_copy": 1,
			"read_only": 1,
			"description": "IMAP 邮件 Message-Id，同步去重键",
		}, ignore_validate=False, is_system_generated=False)
		print("created Mail.message_id")
	# 2) UNIQUE 索引（幂等：已有唯一索引则跳过）
	cur = frappe.db.sql("SHOW INDEX FROM tabMail WHERE Column_name = 'message_id'")
	has_unique = any(r[1] == 0 for r in cur)  # SHOW INDEX 元组第 2 位 Non_unique，0=唯一索引
	if not has_unique:
		frappe.db.sql("ALTER TABLE `tabMail` ADD UNIQUE INDEX `message_id_uniq` (`message_id`)")
		print("added UNIQUE index message_id_uniq")
	else:
		print("unique index already exists")
	frappe.db.commit()
