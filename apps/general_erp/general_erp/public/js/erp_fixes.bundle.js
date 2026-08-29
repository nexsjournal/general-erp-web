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

// 消音 Chart.js 空串颜色告警（P2-3，2026-08-29）：
// 工作区 chart 块（销售订单趋势/采购订单趋势，存量配置）颜色为空串时，
// frappe 打包的 Chart.js validateColors 触发 Blink 打印
// '"" is not a valid color.'（console 噪音，不影响渲染）。
// 精确匹配该告警串过滤，不影响其他 console 警告。
(function () {
	const TARGET = '"" is not a valid color.';
	const _origWarn = console.warn;
	console.warn = function () {
		try {
			if (arguments.length === 1 && String(arguments[0]) === TARGET) return;
		} catch (e) {}
		return _origWarn.apply(console, arguments);
	};
})();

// 工作区改名兼容别名（2026-08-29，T-rename 收口）：
// 「外贸工作台」→「ERP工作台」改名后，用户书签/旧标签/外部链接里的
// /desk/外贸工作台 查不到工作区，页面空/404。router.convert_to_standard_route
// 是 route 解析的唯一漏斗（workspace 查找发生在其内部 line ~176），
// 在漏斗入口把旧名段替换为新名，旧链接自动落到新工作台。仅存在该映射
// 且目标真实存在时生效，不影响其他路由。
(function () {
	const WORKSPACE_ALIASES = { "外贸工作台": "ERP工作台" };
	const key = "__wsAliasGuard";
	const _orig = frappe.router.convert_to_standard_route;
	const _wrapped = async function (route) {
		try {
			if (route && route.length && route[0] && WORKSPACE_ALIASES[route[0]]) {
				const target = frappe.router.slug(WORKSPACE_ALIASES[route[0]]);
				if (frappe.workspaces && frappe.workspaces[target]) {
					route = [target].concat(Array.prototype.slice.call(route, 1));
				}
			}
		} catch (e) {}
		return _orig.call(this, route);
	};
	_wrapped[key] = true;
	frappe.router.convert_to_standard_route = _wrapped;
})();

// 用户表单：生成用户名/密码按钮（T-user-login，2026-08-29）：
// 国内习惯建号——管理员只给用户名+密码，邮箱可不填。
// 用户名=姓名拼音首字母兜底（取 first_name/last_name 前缀），密码=10 位随机。
(function () {
	function genPassword() {
		const chars = "ABCDEFGHJKMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789";
		let s = "";
		for (let i = 0; i < 10; i++) s += chars.charAt(Math.floor(Math.random() * chars.length));
		return s;
	}
	function genUsername(frm) {
		const name = (frm.doc.first_name || frm.doc.username || "user").trim();
		// 已有用户名且非空：保持；否则用姓名
		return name;
	}
	frappe.ui.form.on("User", {
		refresh(frm) {
			if (!frm.fields_dict.username) return;
			frm.add_custom_button(__("生成用户名"), () => {
				frm.set_value("username", genUsername(frm));
				frm.set_value("first_name", genUsername(frm));
				frm.refresh_field("username");
			});
			frm.add_custom_button(__("生成密码"), () => {
				frm.set_value("new_password", genPassword());
				frm.refresh_field("new_password");
			});
		},
	});
})();

// 金额显示口径统一（T-currency，2026-08-29）：
// frappe 图表坐标轴默认走 shorten_number（382,000 → "382 千"），中文场景难读。
// 覆盖 format_chart_axis_number：直接用千分位全称，不再缩写。
(function () {
	const _origAxis = frappe.utils.format_chart_axis_number;
	frappe.utils.format_chart_axis_number = function (label, country) {
		const v = parseFloat(label);
		if (isNaN(v)) return label;
		try {
			return v.toLocaleString("en-US", { maximumFractionDigits: 0 });
		} catch (e) {
			return _origAxis.call(frappe.utils, label, country);
		}
	};
})();

// 数字卡兜底：show_full_number 已数据层开启（site_setup 幂等同步），
// 此处防御旧卡片/未来新增卡片仍走缩写时，shorten_number 不再产出"千/百万"。
(function () {
	const _origShort = frappe.utils.shorten_number;
	frappe.utils.shorten_number = function (number, country, min_length, max_no_of_decimals) {
		const r = _origShort.call(frappe.utils, number, country, min_length, max_no_of_decimals);
		// 结果带中文缩写单位（千/百万/万亿/万/亿）时退回千分位全称
		if (typeof r === "string" && /[千万亿]/.test(r)) {
			const v = parseFloat(number);
			if (!isNaN(v)) {
				try {
					return v.toLocaleString("en-US", { maximumFractionDigits: 2 });
				} catch (e) {
					return r;
				}
			}
		}
		return r;
	};
})();

// T-nav-fix: 导航统一回 首页（金蝶式两级；老 /desk 网格保留给超管维护用）——
// 1) 功能页/模块页顶栏 logo（指向老 /desk 网格）点击 -> 改跳 首页
// 2) 非超管用户直接访问 /desk 裸路由 -> 跳 首页（超管直访仍看老网格）
// 3) 根地址 8002 的 301 由服务端 website_redirects hooks 处理（hooks.py）
(function () {
	const HOME = "/desk/index";
	document.addEventListener("click", function (e) {
		const a = e.target && e.target.closest ? e.target.closest("a[href]") : null;
		if (!a) return;
		let href = null;
		try { href = new URL(a.getAttribute("href"), location.href).pathname; } catch (err) { return; }
		if (href === "/desk" || href === "/desk/") {
			e.preventDefault();
			e.stopPropagation();
			try {
				location.replace(HOME);
			} catch (err2) {
				try { frappe.set_route("index"); } catch (err3) { location.replace(HOME); }
			}
		}
	}, true);
	// 已登录访问 /desk 裸路由 -> 首页（frappe.session 异步就绪，轮询等待，超管保留老网格）
	// T-url-index: /index 短路径 -> 首页（frappe 把 /index 当网站路由返回登录页，这里拦截直达 desk 首页）
	if (location.pathname === "/index") {
		location.replace(HOME);
		return;
	}
	if (location.pathname === "/desk" || location.pathname === "/desk/") {
		const t0 = Date.now();
		const tryRedirect = function () {
			if (location.pathname !== "/desk" && location.pathname !== "/desk/") return;
			const user = (window.frappe && frappe.session) ? frappe.session.user : null;
			if (user && user !== "Guest" && user !== "Administrator") {
				location.replace(HOME);
				return;
			}
			if (Date.now() - t0 > 5000) return;
			setTimeout(tryRedirect, 100);
		};
		setTimeout(tryRedirect, 200);
	}
	// 返回防乱跳守卫：非超管用户浏览器"后退"落回旧 /desk 网格时，自动拉回 首页（index）。
	// 功能页之间的前进/后退不受影响（守卫只在 pathname 变回 /desk 裸路由时生效）。
	window.addEventListener("popstate", function () {
		if (location.pathname !== "/desk" && location.pathname !== "/desk/") return;
		const user = (window.frappe && frappe.session) ? frappe.session.user : null;
		if (user && user !== "Guest" && user !== "Administrator") {
			location.replace(HOME);
		}
	});
})();

// T-brand: 品牌名统一显示为 太康生物ERP（技术模块名 General ERP 保持不变，frappe 按它做 Python 导入）
(function () {
	const BRAND_OLD = "General ERP";
	const BRAND_NEW = "太康生物ERP";
	const applyRebrand = function () {
		// 1) 文案节点替换（侧边栏头/面包屑/表格等）
		try {
			const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null);
			const nodes = [];
			while (walker.nextNode()) {
				if (walker.currentNode.nodeValue && walker.currentNode.nodeValue.indexOf(BRAND_OLD) !== -1) nodes.push(walker.currentNode);
			}
			for (const n of nodes) {
				n.nodeValue = n.nodeValue.split(BRAND_OLD).join(BRAND_NEW);
			}
		} catch (e) { /* ignore */ }
		// 2) title/placeholder 属性
		try {
			document.querySelectorAll('[title="' + BRAND_OLD + '"]').forEach(function (el) { el.setAttribute("title", BRAND_NEW); });
			document.querySelectorAll('[placeholder="' + BRAND_OLD + '"]').forEach(function (el) { el.setAttribute("placeholder", BRAND_NEW); });
		} catch (e) { /* ignore */ }
	};
	// boot 完成后对已渲染内容做一次，并用 MutationObserver 持续覆盖动态渲染
	const start = function () {
		if (!document.body) { setTimeout(start, 100); return; }
		applyRebrand();
		let tick = false;
		const obs = new MutationObserver(function () {
			if (tick) return;
			tick = true;
			setTimeout(function () { tick = false; applyRebrand(); }, 80);
		});
		obs.observe(document.body, { childList: true, subtree: true });
	};
	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", function () { setTimeout(start, 300); });
	} else {
		setTimeout(start, 300);
	}
})();

// T-brand: 浏览器标签页标题带品牌前缀（太康生物ERP - 页面名）
(function () {
	const applyTitle = function () {
		const t = document.title || "";
		if (!t || t === "Login" || t === "login") return;
		// T-url-zh: 首页路由名改为英文 index（防 URL 中文），标签文案仍显示"首页"
		let core = t.indexOf("太康生物ERP - ") === 0 ? t.slice("太康生物ERP - ".length) : t;
		if (core.trim() === "index") { document.title = "太康生物ERP - 首页"; return; }
		if (t.indexOf("太康生物ERP") === -1) {
			document.title = "太康生物ERP - " + t;
		}
	};
	const start = function () {
		if (!document.body) { setTimeout(start, 100); return; }
		applyTitle();
		const obs = new MutationObserver(function () { setTimeout(applyTitle, 120); });
		obs.observe(document.body, { childList: true, subtree: true, characterData: true });
		setInterval(applyTitle, 2000);
	};
	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", function () { setTimeout(start, 400); });
	} else {
		setTimeout(start, 400);
	}
})();

// T-flow-config: 轻量流程配置——每个模块页顶部动态渲染后台可编辑的流程步骤
// 数据源 Module Flow DocType（System Manager 可在 /desk/module-flow 里增删/调序/改链接）
(function () {
	var MODULES = ['销售管理','采购管理','库存管理','财务管理','客户管理','产品管理','邮件中心','外贸管理','生产管理','组织管理','报表中心','系统设置'];

	function resolveModule() {
		try {
			var cp = localStorage.getItem('current_page');
			if (cp && MODULES.indexOf(cp) !== -1) return cp;
			var seg = decodeURIComponent(location.pathname.split('/').pop() || '');
			if (MODULES.indexOf(seg) !== -1) return seg;
			var segRaw = location.pathname.split('/').pop() || '';
			if (frappe.workspace_map) {
				var w = frappe.workspace_map[segRaw] || frappe.workspace_map[seg];
				if (w && MODULES.indexOf(w.name) !== -1) return w.name;
				// 遍历找 slug 匹配
				for (var k in frappe.workspace_map) {
					if (frappe.workspace_map[k] && frappe.workspace_map[k].name === segRaw) {
						if (MODULES.indexOf(frappe.workspace_map[k].name) !== -1) return frappe.workspace_map[k].name;
					}
				}
			}
		} catch (e) {}
		return null;
	}

	function inject() {
		var mod = resolveModule();
		if (!mod) return;
		var workspaceRoot = document.querySelector('.page-body') || document.querySelector('.layout-main');
		if (!workspaceRoot || workspaceRoot.querySelector('.tflow-bar')) return;
		frappe.call({
			method: 'general_erp.general_erp.api_backup.get_module_flow',
			args: { module_name: mod },
			callback: function (res) {
				var data = res && res.message;
				if (!data || !data.steps || !data.steps.length) return;
				var bar = document.createElement('div');
				bar.className = 'tflow-bar';
				bar.style.cssText = 'display:flex;align-items:center;flex-wrap:wrap;gap:6px;margin:8px 0 4px;padding:10px 14px;background:rgba(41,128,185,.07);border:1px solid rgba(41,128,185,.18);border-radius:10px;';
				var label = document.createElement('span');
				label.textContent = '流程：';
				label.style.cssText = 'font-size:13px;font-weight:600;color:#555;margin-right:4px;';
				bar.appendChild(label);
				data.steps.forEach(function (s, i) {
					var chip = document.createElement('span');
					chip.textContent = s.title;
					chip.style.cssText = 'font-size:12.5px;padding:4px 10px;background:#fff;border:1px solid #e0e0e0;border-radius:14px;color:#333;' + (s.link ? 'cursor:pointer;text-decoration:underline;' : '');
					if (s.link) {
						chip.addEventListener('click', function () { frappe.set_route(s.link.replace(/^\//, '').split('/')); });
					}
					if (s.desc) chip.title = s.desc;
					bar.appendChild(chip);
					if (i < data.steps.length - 1) {
						var arrow = document.createElement('span');
						arrow.textContent = '→';
						arrow.style.cssText = 'color:#999;font-size:13px;';
						bar.appendChild(arrow);
					}
				});
				workspaceRoot.insertBefore(bar, workspaceRoot.firstChild);
			}
		});
	}

	if (frappe.router && frappe.router.on) { frappe.router.on('route_change', function () { setTimeout(inject, 1200); }); }
	setInterval(function () { if (location.pathname.indexOf('/desk/') === 0) inject(); }, 3000);
})();
