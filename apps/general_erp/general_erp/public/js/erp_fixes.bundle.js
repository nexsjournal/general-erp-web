/* ============================================================
   general-erp-web 运行期非侵入补丁（JS 侧）
   与 general_erp/__init__.py 的 Python 侧补丁同一约定：
   不改 frappe/erpnext 源码，仅当需要时按语言/场景生效。
   ============================================================ */

// frappe.utils.shorten_number(0) 返回空串 ""，
// 数字卡随后 convert_old_to_new_number_format("") → NaN，显示成 "CNY NaN"。
// 这里保证 0 返回 "0"。
(function () {
	const _orig = frappe.utils.shorten_number;
	frappe.utils.shorten_number = function (number, country, precision) {
		const r = _orig(number, country, precision);
		if (r === "" && (number === 0 || number === "0")) {
			return "0";
		}
		return r;
	};
})();
