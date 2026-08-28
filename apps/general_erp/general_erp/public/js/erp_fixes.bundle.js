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
		const r = _orig.call(frappe.utils, number, country, precision);
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
		if (cached && cached.indexOf("BF_PAGE_V6") === -1) {
			localStorage.removeItem(key);
		}
	} catch (e) {}
})();

// 修复主页"狂闪"（/desk ↔ /desk/setup-wizard 死循环，2026-08-29 T-home-flash 根因）：
//   浏览器 localStorage 残留 session_last_route 指向 setup-wizard（frappe setup 流程写入）。
//   /desk 加载时 desk.js 把它 set_route 过去；setup-wizard 页的构造函数
//   (setup_wizard.js:103) 又无条件 set_route("setup-wizard/0")，on_page_load 又因
//   setup 已完成用 location.href 整页跳回 /desk——反复导航/整页重载 = 白屏狂闪。
//   本补丁（仅 setup 已完成时生效，全新站点不受影响）：
//     ① 加载即清掉指向 setup-wizard 的脏 session_last_route（掐掉种子）；
//     ② 包装 frappe.set_route：目标为 setup-wizard 时改跳主页。set_route 是所有
//        进入该路由的唯一漏斗，掐断后 new SetupWizard 永不成为活跃路由，
//        构造器自推与 on_page_load 整页跳回都不会触发，循环彻底断开。
(function () {
	function isSetupComplete() {
		try {
			if (!frappe.boot) return false;
			return !!(frappe.boot.setup_complete ||
				(frappe.boot.sysdefaults && frappe.boot.sysdefaults.setup_complete));
		} catch (e) { return false; }
	}
	function cleanStaleWizard() {
		try {
			if (!isSetupComplete()) return;
			var slr = localStorage.getItem("session_last_route");
			if (slr && slr.indexOf("setup-wizard") === 0) {
				localStorage.removeItem("session_last_route");
			}
		} catch (e) {}
	}
	function patchSetRoute() {
		if (typeof frappe.set_route !== "function" || frappe.set_route.__flashGuard) return true;
		var orig = frappe.set_route;
		var wrapped = function () {
			try {
				if (isSetupComplete()) {
					var a = Array.prototype.slice.call(arguments);
					var first = a[0];
					var target = (typeof first === "string") ? first
						: (Array.isArray(first) ? (first[0] || "") : "");
					if (String(target).indexOf("setup-wizard") === 0) {
						return orig.apply(this, [ [] ]); // 改跳主页，掐断循环
					}
				}
			} catch (e) {}
			return orig.apply(this, arguments);
		};
		wrapped.__flashGuard = true;
		frappe.set_route = wrapped;
		return true;
	}
	// ① 立即清种子
	cleanStaleWizard();
	// ② frappe.set_route 可能晚于本脚本就绪，轮询兜底（~5s 内挂上），期间周期再清种子
	// 写法避免压缩器改名误伤（2026-08-29 复现过 tries 被截成 ries 的 bug）
	var flashCount = 0;
	var flashTimer = window.setInterval(function () {
		var flashOk = patchSetRoute();
		cleanStaleWizard();
		flashCount = flashCount + 1;
		if (flashOk || flashCount >= 50) {
			window.clearInterval(flashTimer);
		}
	}, 100);
})();

// 客户表单"移交"按钮：变更负责人并留痕（Customer Follow Up 模块 whitelisted 方法）。
(function () {
	frappe.ui.form.on("Customer", {
		refresh(frm) {
			if (frm.doc.__islocal || !frm.doc.name) return;
			frm.add_custom_button(__("移交"), () => {
				const d = new frappe.ui.Dialog({
					title: __("移交客户"),
					fields: [
						{ fieldname: "to_user", fieldtype: "Link", label: __("移交至"), options: "User", reqd: 1 },
						{ fieldname: "remark", fieldtype: "Small Text", label: __("原因/备注") },
					],
					primary_action(values) {
						frappe.call({
							method: "general_erp.general_erp.doctype.customer_follow_up.customer_follow_up.handover_customer",
							args: { name: frm.doc.name, to_user: values.to_user, remark: values.remark },
							callback() {
								frappe.msgprint(__("移交成功，已留痕。"));
								d.hide();
								frm.reload_doc();
							},
						});
					},
				});
				d.show();
			});
		},
	});
})();

// 线索表单"分发"按钮：分派被分发人并写入 Lead Distribution Log。
(function () {
	frappe.ui.form.on("Lead", {
		refresh(frm) {
			if (frm.doc.__islocal || !frm.doc.name) return;
			frm.add_custom_button(__("分发"), () => {
				const d = new frappe.ui.Dialog({
					title: __("分发线索"),
					fields: [
						{ fieldname: "to_user", fieldtype: "Link", label: __("分发给"), options: "User", reqd: 1 },
						{ fieldname: "remark", fieldtype: "Small Text", label: __("备注") },
					],
					primary_action(values) {
						frappe.call({
							method: "general_erp.general_erp.doctype.lead_distribution_log.lead_distribution_log.assign_lead",
							args: { name: frm.doc.name, to_user: values.to_user, remark: values.remark },
							callback() {
								frappe.msgprint(__("分发成功，已写入分发记录。"));
								d.hide();
								frm.reload_doc();
							},
						});
					},
				});
				d.show();
			});
		},
	});
})();

// 客户表单"360 视图"按钮：跳转客户 360 聚合页（跟进/商机/报价/订单/邮件）。
(function () {
	frappe.ui.form.on("Customer", {
		refresh(frm) {
			if (frm.doc.__islocal || !frm.doc.name) return;
			frm.add_custom_button(__("360 视图"), () => {
				frappe.route_options = { customer: frm.doc.name };
				frappe.set_route("desk", "customer-360");
			});
		},
	});
})();
