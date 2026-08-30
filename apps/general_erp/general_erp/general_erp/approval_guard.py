# -*- coding: utf-8 -*-
"""T14: 审批工作流防绕过守卫（frappe v16 补丁）

背景：frappe v16 工作流的"审批中"状态若映射 doc_status=0，
提交人在"审批中"直接点原生 Submit 会把 docstatus 置 1，
工作流再按 doc_status=1 把状态自动跳到"已审批"，
boss 的审批环节被完全绕过（graph 测试 P1：生产任务单/采购订单）。

方案（非侵入，只在本 app 的 doc_events 挂守卫）：
1. before_submit: 单据处于审批链中间态（如审批中）且当前用户
   不具"下一跳"审批角色、也没有 Workflow Action 完成留痕 → 拒绝提交。
   Administrator 放行（超管/脚本/回归处理需要）。
2. before_save: 提交态单据的工作流状态被从"审批中"直接改成终态
   "已审批"（未经 Workflow Action）→ 拒绝保存。

本守卫只在"存在活跃工作流 + 单据处于中间审批态"时生效，
普通无审批单据、草稿态提交、费用报销（审批中=doc_status=1 本就能卡住）不受影响。
"""

import frappe
from frappe import _

# 视为"审批完成"的终态
FINAL_STATES = ("已审批",)
# 视为"还在审批链中间"的状态（需要守卫）
MIDDLE_STATES = ("审批中",)


def _get_workflow(doctype):
    try:
        from frappe.model.workflow import get_workflow

        return get_workflow(doctype)
    except Exception:
        return None


def _current_state(doc):
    wf = _get_workflow(doc.doctype)
    if not wf:
        return None, None
    state = doc.get(wf.workflow_state_field)
    if not state:
        return wf, None
    return wf, state


def _is_middle_state(state):
	"""审批中 / 审批1 / 审批2 …（向导多级审批状态）都算审批链中间态"""
	return bool(state) and state.startswith("审批") and state != "已审批"


def _allowed_roles_for_next(wf, state):
    """当前状态可执行动作（下一跳）的允许角色并集"""
    roles = set()
    for t in wf.transitions:
        if t.state == state:
            roles.add(t.allowed)
    return roles


def _has_transition_completed_by_user(doctype, docname, user):
    """该用户是否在"审批中间态"完成过 Workflow Action（合法审批留痕）

    注意：提交人自己完成"提交审批"（草稿→审批中）也留有 Workflow Action，
    因此必须限定 workflow_state 在中间态内，才算审批动作留痕。
    """
    if not docname:
        return False
    return frappe.db.exists(
        "Workflow Action",
        {
            "reference_doctype": doctype,
            "reference_name": docname,
            "completed_by": user,
            "workflow_state": ("like", "审批%"),
        },
    )


def guard_before_submit(doc, method=None):
    """审批中单据禁止提交人自己 Submit 绕过审批"""
    if not doc.get("name"):
        return
    wf = _get_workflow(doc.doctype)
    if not wf:
        return
    # 以【数据库里的】工作流状态判别：
    # 合法首次提交（草稿→审批1）时库里还是草稿 → 放行；
    # 库里已是审批中间态（单据已提交进审批链）再 submit/改态 → 需要审批角色。
    db_state = frappe.db.get_value(doc.doctype, doc.get("name"), wf.workflow_state_field)
    if not _is_middle_state(db_state):
        return
    # Workflow Action 发起的保存（审批动作本身）放行
    if getattr(doc.flags, "in_workflow_action", False):
        return
    user = frappe.session.user
    if user == "Administrator":
        return
    roles = set(frappe.get_roles(user))
    if not roles:
        return
    # 已执行过 Workflow Action 的用户（合法审批人）放行
    if _has_transition_completed_by_user(doc.doctype, doc.get("name"), user):
        return
    # 用户具备"下一跳"审批角色（如经理）——允许其 Submit 推进
    next_roles = _allowed_roles_for_next(wf, db_state)
    if next_roles and next_roles.isdisjoint(roles):
        frappe.throw(
            _("该单据正在审批中，无法直接提交。请等待审批人处理。"),
            title=_("审批中，禁止绕过审批提交"),
        )


def guard_before_save(doc, method=None):
    """提交态单据：库里还停在审批中间态时，操作者必须是该跳的允许角色

    与 before_submit 互补：before_submit 覆盖 .submit() 调用路径；
    本守卫覆盖"直接 docstatus=1 + 改 workflow_state 后 save"的绕过路径
    （包括 API 直改字段提交）。合法审批人（在中间态"下一跳"允许角色并集内）
    放行；提交人自己推进则拒绝。Administrator 放行。
    """
    if getattr(doc, "docstatus", 0) != 1:
        return
    if not doc.get("name"):
        return
    wf = _get_workflow(doc.doctype)
    if not wf:
        return
    db_state = frappe.db.get_value(doc.doctype, doc.get("name"), wf.workflow_state_field)
    if not _is_middle_state(db_state):
        return
    user = frappe.session.user
    if user == "Administrator":
        return
    # 有该用户在中间态完成的 Workflow Action 留痕 = 合法审批
    if _has_transition_completed_by_user(doc.doctype, doc.get("name"), user):
        return
    # 用户在中间态"下一跳"允许角色并集内（合法审批人）放行
    roles = set(frappe.get_roles(user))
    mid_roles = _allowed_roles_for_next(wf, db_state)
    if roles and mid_roles and not mid_roles.isdisjoint(roles):
        return
    frappe.throw(
        f"该单据当前处于{db_state}，无法直接提交为已提交/已审批状态。请等待审批人处理。",
        title="审批中，禁止绕过审批",
    )


def guard_purchase_receipt(doc, method=None):
    """收货单提交/保存时，关联采购订单必须处于"已审批"，防止审批中的 PO 过账库存"""
    rows = doc.get("items") or []
    checked = set()
    for row in rows:
        po = row.get("purchase_order")
        if not po or po in checked:
            continue
        checked.add(po)
        ws_field = "workflow_state"
        wf = _get_workflow("Purchase Order")
        if wf:
            ws_field = wf.workflow_state_field
        state = frappe.db.get_value("Purchase Order", po, ws_field)
        if state and state != "已审批":
            frappe.throw(
                f"采购订单 {po} 当前状态为{state}（未审批完成），不能生成收货单过账。请先完成审批。",
                title="未审批订单禁止收货",
            )
