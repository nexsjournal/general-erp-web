# -*- coding: utf-8 -*-
"""数据备份 API：仅 System Manager 可操作。备份文件在 sites/<site>/private/backups"""
import frappe
import os
import glob
from datetime import datetime
from frappe import _


def _backup_dir():
    return os.path.abspath(frappe.get_site_path("private", "backups"))


def _check_permission():
    if "System Manager" not in frappe.get_roles():
        frappe.throw(_("仅系统管理员可操作备份"), frappe.PermissionError)


def _list_files():
    d = _backup_dir()
    files = []
    if os.path.isdir(d):
        for f in sorted(glob.glob(os.path.join(d, "*.sql.gz")), key=os.path.getmtime, reverse=True):
            files.append({
                "filename": os.path.basename(f),
                "size_mb": round(os.path.getsize(f) / 1024 / 1024, 2),
                "created": frappe.utils.format_datetime(datetime.fromtimestamp(os.path.getmtime(f))),
            })
    return files


@frappe.whitelist()
def get_backup_list():
    _check_permission()
    return _list_files()


@frappe.whitelist()
def trigger_backup():
    _check_permission()
    from frappe.utils.backups import scheduled_backup
    scheduled_backup(ignore_files=True, verbose=False, force=True)
    files = _list_files()
    latest = files[0] if files else None
    return {
        "success": True,
        "message": _("备份成功"),
        "file": latest["filename"] if latest else None,
        "size_mb": latest["size_mb"] if latest else 0,
    }


@frappe.whitelist()
def download_backup(filename):
    """流式下载备份文件（cookie 鉴权 + System Manager 校验，防路径穿越）"""
    _check_permission()
    filename = os.path.basename(filename or "")
    if not filename or not filename.endswith(".sql.gz"):
        frappe.throw(_("非法文件名"))
    full = os.path.join(_backup_dir(), filename)
    if not os.path.isfile(full):
        frappe.throw(_("备份文件不存在"))
    with open(full, "rb") as fp:
        content = fp.read()
    from frappe.utils.response import downloadfile
    downloadfile(filename, content)


# ---------- 模块流程配置（轻量版：后台可编辑步骤+调序） ----------
@frappe.whitelist()
def get_module_flow(module_name):
    """用户端读取某模块的流程步骤（所有登录用户可读）"""
    if not module_name:
        return None
    name = frappe.db.get_value("Module Flow", {"module_name": module_name, "enabled": 1}, "name")
    if not name:
        return None
    d = frappe.get_doc("Module Flow", name)
    return {
        "module_name": d.module_name,
        "flow_title": d.flow_title,
        "steps": [
            {"title": s.step_title, "desc": s.step_desc, "link": s.link_to}
            for s in d.steps
        ],
    }
