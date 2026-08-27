/* 区域设置：时区 / 语言 / 日期格式 / 区域显示（System Settings + 用户偏好 + 公司默认） */

const RS = {
	async load() {
		const [sys, gd] = await Promise.all([
			frappe.db.get_doc('System Settings', 'System Settings'),
			frappe.db.get_doc('Global Defaults', 'Global Defaults'),
		]);
		const me = await frappe.db.get_doc('User', frappe.session.user);
		document.getElementById('rs-lang').value = sys.language || 'zh';
		document.getElementById('rs-tz').value = sys.time_zone || 'Asia/Shanghai';
		document.getElementById('rs-df').value = sys.date_format || 'YYYY-MM-DD';
		document.getElementById('rs-mlang').value = me.language || 'zh';
		document.getElementById('rs-mtz').value = me.time_zone || '';
		document.getElementById('rs-mdf').value = me.date_format || '';
		document.getElementById('rs-company').textContent = gd.default_company || '—';
		document.getElementById('rs-currency').textContent = gd.default_currency || '—';
		document.getElementById('rs-country').textContent = gd.country || '—';
	},

	saveSys() {
		frappe.db.set_single('System Settings', {
			language: document.getElementById('rs-lang').value,
			time_zone: document.getElementById('rs-tz').value,
			date_format: document.getElementById('rs-df').value,
		}).then(() => frappe.show_alert({ indicator: 'green', message: __('系统区域设置已保存（刷新页面生效）') }));
	},

	saveUser() {
		frappe.db.set_value('User', frappe.session.user, {
			language: document.getElementById('rs-mlang').value,
			time_zone: document.getElementById('rs-mtz').value,
			date_format: document.getElementById('rs-mdf').value,
		}).then(() => frappe.show_alert({ indicator: 'green', message: __('个人偏好已保存') }));
	},

	setLang(lang) {
		frappe.db.set_value('User', frappe.session.user, { language: lang }).then(() => location.reload());
	},
};

function make(wrapper) {
	wrapper.innerHTML = `
		<div class="rs-wrap">
			<div class="rs-head">
				<div class="rs-title">${__('区域设置')}</div>
				<div class="rs-subtitle">${__('时区 · 语言 · 日期格式 · 区域显示 —— 系统级与个人级配置（中英文配置）')}</div>
			</div>
			<div class="rs-grid">
				<div class="card">
					<div class="rs-sec">${__('系统区域')}（System Settings，管理员生效）</div>
					<div class="rs-field"><label>${__('界面语言')}</label><select id="rs-lang" class="rs-select"><option value="zh">中文</option><option value="en">English</option></select></div>
					<div class="rs-field"><label>${__('时区')}</label><select id="rs-tz" class="rs-select"><option>Asia/Shanghai</option><option>UTC</option><option>Asia/Tokyo</option><option>Europe/Berlin</option><option>America/New_York</option></select></div>
					<div class="rs-field"><label>${__('日期格式')}</label><select id="rs-df" class="rs-select"><option>YYYY-MM-DD</option><option>DD/MM/YYYY</option><option>MM/DD/YYYY</option><option>DD-MM-YYYY</option></select></div>
					<button class="btn btn-primary btn-sm rs-save-sys">${__('保存系统设置')}</button>
				</div>
				<div class="card">
					<div class="rs-sec">${__('个人偏好')}（当前用户）</div>
					<div class="rs-field"><label>${__('语言')}</label><select id="rs-mlang" class="rs-select"><option value="zh">中文</option><option value="en">English</option><option value="">跟随系统</option></select></div>
					<div class="rs-field"><label>${__('时区')}</label><select id="rs-mtz" class="rs-select"><option value="">默认</option><option>Asia/Shanghai</option><option>UTC</option><option>Asia/Tokyo</option><option>Europe/Berlin</option><option>America/New_York</option></select></div>
					<div class="rs-field"><label>${__('日期格式')}</label><select id="rs-mdf" class="rs-select"><option value="">默认</option><option>YYYY-MM-DD</option><option>DD/MM/YYYY</option><option>MM/DD/YYYY</option></select></div>
					<button class="btn btn-primary btn-sm rs-save-user">${__('保存个人偏好')}</button>
					<div class="rs-quick">
						<span>${__('快速切换：')}</span>
						<button class="btn btn-sm rs-lang-btn" data-lang="zh">中文</button>
						<button class="btn btn-sm rs-lang-btn" data-lang="en">English</button>
					</div>
				</div>
				<div class="card">
					<div class="rs-sec">${__('公司默认')}（Global Defaults）</div>
					<div class="rs-field"><label>${__('默认公司')}</label><span class="rs-val" id="rs-company">—</span></div>
					<div class="rs-field"><label>${__('本位币')}</label><span class="rs-val" id="rs-currency">—</span></div>
					<div class="rs-field"><label>${__('国家/地区')}</label><span class="rs-val" id="rs-country">—</span></div>
					<button class="btn btn-sm" onclick="frappe.set_route('desk','global-defaults')">${__('打开全局默认值')}</button>
				</div>
			</div>
		</div>`;

	wrapper.querySelector('.rs-save-sys').addEventListener('click', () => RS.saveSys());
	wrapper.querySelector('.rs-save-user').addEventListener('click', () => RS.saveUser());
	wrapper.querySelectorAll('.rs-lang-btn').forEach(b => b.addEventListener('click', () => RS.setLang(b.dataset.lang)));
	RS.load();
}

frappe.pages['regional-settings'].on_page_load = function (wrapper) {
	make(wrapper);
};
