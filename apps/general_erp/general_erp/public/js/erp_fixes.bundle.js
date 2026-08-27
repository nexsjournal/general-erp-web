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

// 表单右侧栏标题走 get_doc_title → String(doc.name)，不经翻译，
// 导致单例 DocType（如 Global Defaults）标题显示英文。返回值统一走 __()。
(function () {
	const _orig = frappe.model.get_doc_title;
	frappe.model.get_doc_title = function (doc) {
		const t = _orig(doc);
		return typeof __ === "function" && t ? __(t) : t;
	};
})();

// frappe 的 doctype 路由表按小写 slug 注册（setup() 内 this.routes[slug]），
// 大写/含空格路由（/desk/Customer、set_route(['desk','Sales Order'])）匹配不到，
// 会回退到"页面"查找并报"页面 xxx 未找到"。这里在路由解析前统一归一化为 slug。
(function () {
	if (!frappe.router || !frappe.router.convert_to_standard_route) return;
	const _orig = frappe.router.convert_to_standard_route;
	frappe.router.convert_to_standard_route = function (route) {
		try {
			if (route && route.length && this.routes) {
				const seg = route[0];
				if (typeof seg === "string" && !this.routes[seg]) {
					const slug = seg.toLowerCase().replace(/ /g, "-");
					if (slug !== seg && this.routes[slug]) {
						route[0] = slug;
					}
				}
			}
		} catch (e) {
			// 补丁异常不影响主路由流程
		}
		return _orig.call(this, route);
	};
})();

// frappe desk 将页面脚本缓存于 localStorage（_page:<page>）且无版本校验，
// 页面脚本更新后旧缓存会一直生效。检测到无新版本标记的旧缓存时删除，强制拉取最新。
(function () {
	try {
		const key = "_page:business-flow";
		const cached = localStorage.getItem(key);
		if (cached && cached.indexOf("BF_PAGE_V2") === -1) {
			localStorage.removeItem(key);
		}
	} catch (e) {}
})();
