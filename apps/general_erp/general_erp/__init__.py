__version__ = "0.1.0"

# ============================================================
# 中文本地化：Desk 趋势图 / 趋势报表的周期标签（运行期非侵入替换）
# 1) frappe.utils.dateutils.get_period 对 Monthly/Quarterly 硬编码
#    英文（"Jan 2026"/"Quarter 1 2026"），Desk 图表数据直接用它。
# 2) erpnext.controllers.trends.get_mon 用 strftime("%b") 生成
#    月份标签（"Jan"），各 *Trends 报表的 x 轴都来自它。
# 二者都无法通过翻译表覆盖，这里在不改 frappe/erpnext 源码的
# 前提下做运行期替换，仅当请求语言为中文时生效。
# 注意：此文件随 hooks.py 加载而导入，保持导入轻量、无 DB 访问。
# ============================================================
import frappe
import frappe.utils.dateutils as _dateutils
from frappe.utils import getdate as _getdate

_original_get_period = _dateutils.get_period


def _localized_get_period(date, interval="Monthly"):
	result = _original_get_period(date, interval)
	lang = (getattr(frappe.local, "lang", None) or "").lower()
	if not lang.startswith("zh"):
		return result
	if interval == "Monthly":
		return f"{_getdate(date).month}月 {result.split()[-1]}"
	if interval == "Quarterly":
		return result.replace("Quarter", "Q", 1)
	return result


_dateutils.get_period = _localized_get_period


def _is_zh_request():
	return (getattr(frappe.local, "lang", None) or "").lower().startswith("zh")


class _TrendsMonthPatcher:
	"""首次导入 erpnext.controllers.trends 时给 get_mon 打中文补丁。"""

	def find_spec(self, fullname, path=None, target=None):
		if fullname != "erpnext.controllers.trends":
			return None
		import importlib.util
		import sys

		sys.meta_path.remove(self)
		spec = importlib.util.find_spec(fullname)
		original_exec = spec.loader.exec_module

		def exec_module(module):
			original_exec(module)
			original_get_mon = module.get_mon

			def get_mon(dt):
				if _is_zh_request():
					return f"{_getdate(dt).month}月"
				return original_get_mon(dt)

			module.get_mon = get_mon

		spec.loader.exec_module = exec_module
		return spec


import sys as _sys

_sys.meta_path.insert(0, _TrendsMonthPatcher())


# ============================================================
# 错误码统一 422（T2-08 / T2-12 加固）
# frappe 默认 ValidationError.http_status_code = 417。
# 产品对外统一为 422（业务校验失败语义更清晰），脱敏由前端/safe_call 负责。
# 不改 frappe 源码，仅运行期改类属性；带版本断言：frappe 大版本变化时告警。
# ============================================================

EXPECTED_FRAPPE_VERSION_PREFIX = "16."


_runtime_version_guard_done = False


def _version_guard(patch_name):
	global _runtime_version_guard_done
	if _runtime_version_guard_done:
		return
	_runtime_version_guard_done = True
	version = getattr(frappe, "__version__", "unknown")
	if not str(version).startswith(EXPECTED_FRAPPE_VERSION_PREFIX):
		try:
			frappe.logger().warning(
				"general_erp runtime patches loaded against frappe "
				+ str(version) + " (expected " + EXPECTED_FRAPPE_VERSION_PREFIX
				+ "x). Verify patches still work after upgrade: [" + patch_name + "]"
			)
		except Exception:
			pass


try:
	if getattr(frappe.exceptions.ValidationError, "http_status_code", None) != 422:
		frappe.exceptions.ValidationError.http_status_code = 422
	_version_guard("ValidationError->422")
except Exception:
	pass
