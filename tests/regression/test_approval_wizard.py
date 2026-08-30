# -*- coding: utf-8 -*-
"""T-approval-wizard 回归：审批设置向导 API 闭环。

覆盖：① 两级流程生成（状态/流转/免批条件/催办字段）
      ② 小额免批 condition 正确性
      ③ 非法单据类型拦截
      ④ 审批链 e2e（提交审批→守卫拦绕过→审批人通过）
      ⑤ 同 doctype 互斥（新流程启用时旧流程置停用）
测试数据带 TAG 前缀，结束自清理。
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import *  # noqa

import json


def main():
    connect()
    r = Results()
    import general_erp.api_approval_wizard as aw
    # 环境自愈：确保向导依赖的 State/Action/Custom Field 存在（幂等）
    from general_erp.general_erp.site_setup import sync_approval_wizard
    sync_approval_wizard()

    # 清掉旧测试流程
    for n in frappe.get_all("Workflow", filters={"name": ["like", "审批-%"]}, pluck="name"):
        try:
            d = frappe.get_doc("Workflow", n)
            d.flags.ignore_permissions = True
            d.delete()
            frappe.db.commit()
        except Exception:
            pass

    # ① 两级流程 + 免批 + 催办
    try:
        w = aw.save_workflow("", "Sales Order", json.dumps(["Sales User"]),
                             json.dumps([{"roles": ["Sales Manager"]}, {"roles": ["总经理"]}]),
                             1, "5000", "24", 1)
        assert len(w["chain"]) == 2, w["chain"]
        assert w["min_approval_amount"] == 5000.0
        assert w["approval_timeout_hours"] == 24
        assert w["start_role_labels"] == ["销售"]
        # 免批流转 condition 校验
        doc = frappe.get_doc("Workflow", w["name"])
        cond_rows = [t for t in doc.transitions if t.action == "免批通过"]
        assert len(cond_rows) == 1 and "grand_total" in cond_rows[0].condition and "5000" in cond_rows[0].condition
        r.ok("向导-两级流程生成", "状态%d 流转%d min=5000" % (len(doc.states), len(doc.transitions)))
    except Exception as e:
        r.fail("向导-两级流程生成", e)

    # ③ 非法单据拦截
    try:
        aw.save_workflow("", "NonExistent DT", json.dumps(["Sales User"]),
                         json.dumps([{"roles": ["Sales Manager"]}]), 0, "", "24", 1)
        r.fail("向导-非法单据拦截", "未拦截")
    except frappe.exceptions.ValidationError:
        frappe.db.rollback()
        r.ok("向导-非法单据拦截", "抛出 ValidationError")

    # ⑤ 同 doctype 互斥：对 Sales Order 再建一条（不同发起角色），第一条应被停用
    try:
        w2 = aw.save_workflow("", "Sales Order", json.dumps(["Sales User", "Accounts User"]),
                              json.dumps([{"roles": ["Sales Manager"]}]), 0, "", "24", 1)
        frappe.db.commit()
        # 同单据只有"审批-Sales Order"一个名字（覆盖式），active=1
        actives = frappe.get_all("Workflow", filters={"document_type": "Sales Order", "is_active": 1}, pluck="name")
        assert len(actives) == 1, actives
        r.ok("向导-同单据唯一生效流程", "active=%s" % actives)
    except Exception as e:
        r.fail("向导-同单据唯一生效流程", e)

    # ④ e2e：采购员提交 → 守卫拦绕过 → 审批人通过
    # 用一个干净 doctype 避免动采购订单审批（预置流程回归依赖它）
    try:
        for n in frappe.get_all("Workflow", filters={"name": ["like", "审批-%"]}, pluck="name"):
            d = frappe.get_doc("Workflow", n); d.flags.ignore_permissions = True; d.delete()
            frappe.db.commit()
        aw.save_workflow("", "Purchase Order", json.dumps(["Purchase User"]),
                         json.dumps([{"roles": ["Sales Manager"]}]), 0, "", "24", 1)
        frappe.clear_cache()
        # 造 PO
        frappe.set_user("purchase1@demo.com")
        po = frappe.new_doc("Purchase Order")
        po.update(dict(supplier="深圳华强电子供应商", supplier_name="深圳华强电子供应商",
                       company=COMPANY, title=TAG, schedule_date=TODAY,
                       naming_series="PO-.FWS.-.#####.", set_warehouse=WH))
        po.append("items", dict(item_code=ITEM, qty=2, rate=100, warehouse=WH))
        po.insert(); frappe.db.commit()
        from frappe.model.workflow import apply_workflow
        apply_workflow(json.dumps({"doctype": "Purchase Order", "name": po.name}), "提交审批")
        frappe.db.commit()
        st1 = frappe.db.get_value("Purchase Order", po.name, "workflow_state")
        assert st1 == "审批1", st1
        # 守卫：提交人偷改状态为已审批 → 拒
        try:
            d = frappe.get_doc("Purchase Order", po.name)
            d.flags.ignore_permissions = True
            d.workflow_state = "已审批"
            d.save(); frappe.db.commit()
            r.fail("向导-e2e绕过拦截", "未拦截")
        except frappe.exceptions.ValidationError:
            frappe.db.rollback()
        # 审批人通过
        frappe.set_user("boss1@demo.com")
        apply_workflow(json.dumps({"doctype": "Purchase Order", "name": po.name}), "审批通过")
        frappe.db.commit()
        st2 = frappe.db.get_value("Purchase Order", po.name, "workflow_state")
        assert st2 == "已审批", st2
        # 清理 PO
        frappe.set_user("Administrator")
        d = frappe.get_doc("Purchase Order", po.name)
        d.flags.ignore_permissions = True
        try:
            d.cancel(); frappe.db.commit()
        except Exception:
            frappe.db.rollback()
        try:
            d.delete(); frappe.db.commit()
        except Exception:
            pass
        r.ok("向导-e2e审批链", "提交→拦截绕过→审批通过 全通")
    except Exception as e:
        r.fail("向导-e2e审批链", e)

    # 清理：删测试流程 + 恢复预置 采购订单审批 active
    for n in frappe.get_all("Workflow", filters={"name": ["like", "审批-%"]}, pluck="name"):
        try:
            d = frappe.get_doc("Workflow", n); d.flags.ignore_permissions = True; d.delete()
            frappe.db.commit()
        except Exception:
            pass
    preset = frappe.db.exists("Workflow", "采购订单审批")
    if preset:
        d = frappe.get_doc("Workflow", "采购订单审批")
        if not d.is_active:
            d.is_active = 1
            d.flags.ignore_permissions = True
            d.save(); frappe.db.commit()
    frappe.clear_cache()
    return r.summary()


if __name__ == "__main__":
    sys.exit(main())

