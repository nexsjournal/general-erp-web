# -*- coding: utf-8 -*-
import frappe
from frappe import _


def execute(filters=None):
	from general_erp.general_erp.report_utils import check_report_access
	check_report_access("批次统计")
	"""批次库存统计：批次、商品、批次库存、仓库、生产日期、失效日期。

	兼容两种批次存储：
	- 旧口径：SLE.batch_no 直接有值（未启用 Serial and Batch Bundle）
	- v16 口径：批次存于 Serial and Batch Bundle 子表，SLE.serial_and_batch_bundle 指向 bundle，
	  子表 Serial and Batch Entry 按 is_outward 标记出入方向（inward 正 / outward 负）
	两条路径 UNION 后按 批次+商品+仓库 聚合净库存，过滤 0 库存。
	"""
	rows = frappe.db.sql(
		"""SELECT src.batch_no AS batch_no, src.item AS item,
			i.item_name AS item_name, src.warehouse AS warehouse,
			SUM(src.qty) AS qty, bt.manufacturing_date, bt.expiry_date
		FROM (
			SELECT sle.batch_no AS batch_no, sle.item_code AS item,
				sle.warehouse AS warehouse, sle.actual_qty AS qty
			FROM `tabStock Ledger Entry` sle
			WHERE sle.batch_no IS NOT NULL AND sle.batch_no != ''
			UNION ALL
			SELECT sbe.batch_no AS batch_no, sbe.item_code AS item,
				sbe.warehouse AS warehouse,
				CASE WHEN sbe.is_outward = 1 THEN -sbe.qty ELSE sbe.qty END AS qty
			FROM `tabSerial and Batch Entry` sbe
			JOIN `tabStock Ledger Entry` sle2 ON sle2.serial_and_batch_bundle = sbe.parent
			WHERE sbe.batch_no IS NOT NULL AND sbe.batch_no != ''
		) src
		LEFT JOIN `tabItem` i ON i.name = src.item
		LEFT JOIN `tabBatch` bt ON bt.name = src.batch_no
		GROUP BY src.batch_no, src.item, src.warehouse
		HAVING SUM(src.qty) <> 0
		ORDER BY bt.manufacturing_date DESC, src.item""",
		as_dict=True)
	data = [{
		"batch_no": r.batch_no, "item": r.item, "item_name": r.item_name or "",
		"warehouse": r.warehouse or "", "qty": r.qty or 0,
		"manufacturing_date": str(r.manufacturing_date or ""), "expiry_date": str(r.expiry_date or ""),
	} for r in rows]
	columns = [
		{"label": _("批次号"), "fieldname": "batch_no", "fieldtype": "Data"},
		{"label": _("商品"), "fieldname": "item", "fieldtype": "Link", "options": "Item"},
		{"label": _("商品名称"), "fieldname": "item_name", "fieldtype": "Data"},
		{"label": _("仓库"), "fieldname": "warehouse", "fieldtype": "Data"},
		{"label": _("批次库存"), "fieldname": "qty", "fieldtype": "Float"},
		{"label": _("生产日期"), "fieldname": "manufacturing_date", "fieldtype": "Data"},
		{"label": _("失效日期"), "fieldname": "expiry_date", "fieldtype": "Data"},
	]
	return columns, data
