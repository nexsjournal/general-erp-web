/* 工作日历：月/周视图，聚合节假日 · 跟进提醒 · 出运计划 · 商机成交 · 工作检查 */

const CAL = {
	year: 0,
	month: 0,
	weekStart: null,
	view: 'month',
	events: [],

	init() {
		const now = new Date();
		this.year = now.getFullYear();
		this.month = now.getMonth() + 1;
		this.weekStart = frappe.datetime.add_days(frappe.datetime.nowdate(), -new Date().getDay());
	},

	typeMeta() {
		return {
			holiday: { label: __('节假日'), color: '#f53f3f', icon: '🏖' },
			follow: { label: __('跟进提醒'), color: '#2563eb', icon: '📞' },
			shipment: { label: __('出运计划'), color: '#0fc6c2', icon: '🚢' },
			opportunity: { label: __('商机成交'), color: '#722ed1', icon: '🎯' },
			work_check: { label: __('工作检查'), color: '#d97706', icon: '✅' },
		};
	},

	async load() {
		const loadingEl = document.querySelector('.cal-loading');
		if (loadingEl) loadingEl.textContent = __('加载中…');
		if (this.view === 'month') {
			this.events = await frappe.xcall('general_erp.general_erp.calendar_utils.get_calendar_events', { year: this.year, month: this.month });
		} else {
			const start = this.weekStart;
			const end = frappe.datetime.add_days(start, 7);
			const y = parseInt(start.slice(0, 4)), m = parseInt(start.slice(5, 7));
			const y2 = parseInt(end.slice(0, 4)), m2 = parseInt(end.slice(5, 7));
			const a = await frappe.xcall('general_erp.general_erp.calendar_utils.get_calendar_events', { year: y, month: m });
			const b = (y2 !== y || m2 !== m) ? await frappe.xcall('general_erp.general_erp.calendar_utils.get_calendar_events', { year: y2, month: m2 }) : [];
			this.events = [...a, ...b].filter(e => e.date >= start && e.date < frappe.datetime.add_days(end, 1));
		}
		this.render();
	},

	render() {
		const meta = this.typeMeta();
		const main = document.querySelector('.cal-main');
		const title = this.view === 'month'
			? `${this.year} ${__('年')} ${this.month} ${__('月')}`
			: `${__('周视图')} · ${this.weekStart} ${__('起')}`;
		document.querySelector('.cal-title').textContent = title;

		if (this.view === 'month') {
			const first = new Date(this.year, this.month - 1, 1);
			const days = new Date(this.year, this.month, 0).getDate();
			let startDow = first.getDay();
			const cells = [];
			for (let i = 0; i < startDow; i++) cells.push('<div class="cal-cell cal-other"></div>');
			for (let d = 1; d <= days; d++) {
				const iso = `${this.year}-${String(this.month).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
				const evs = this.events.filter(e => e.date === iso);
				const isToday = iso === frappe.datetime.nowdate();
				cells.push(`
					<div class="cal-cell${isToday ? ' is-today' : ''}" data-date="${iso}">
						<div class="cal-daynum">${d}</div>
						<div class="cal-evs">${evs.map(e => `<div class="cal-ev" style="border-color:${meta[e.type].color}" title="${e.label}">${meta[e.type].icon} ${this.shortLabel(e.label)}</div>`).join('')}</div>
					</div>`);
			}
			main.innerHTML = `
				<div class="cal-grid cal-weekdays">${[__('日'), __('一'), __('二'), __('三'), __('四'), __('五'), __('六')].map(w => `<div>${w}</div>`).join('')}</div>
				<div class="cal-grid">${cells.join('')}</div>`;
		} else {
			const days = [];
			for (let i = 0; i < 7; i++) days.push(frappe.datetime.add_days(this.weekStart, i));
			main.innerHTML = days.map(iso => {
				const evs = this.events.filter(e => e.date === iso);
				const isToday = iso === frappe.datetime.nowdate();
				return `
					<div class="cal-week-row${isToday ? ' is-today' : ''}">
						<div class="cal-week-date">${iso}</div>
						<div class="cal-week-evs">${evs.length ? evs.map(e => `<div class="cal-ev" style="border-color:${meta[e.type].color}">${meta[e.type].icon} ${e.label}</div>`).join('') : '<span class="cal-none">—</span>'}</div>
					</div>`;
			}).join('');
		}

		// 图例
		document.querySelector('.cal-legend').innerHTML = Object.values(meta).map(m =>
			`<span class="cal-lg"><span class="cal-dot" style="background:${m.color}"></span>${m.label}</span>`).join('');

		main.querySelectorAll('.cal-cell[data-date]').forEach(cell => {
			cell.addEventListener('click', () => {
				const evs = this.events.filter(e => e.date === cell.dataset.date);
				if (!evs.length) return;
				frappe.msgprint(evs.map(e => `${e.label}（${e.date}）`).join('<br>'), cell.dataset.date);
			});
		});
	},

	shortLabel(s) {
		return s.length > 10 ? s.slice(0, 10) + '…' : s;
	},

	prev() {
		if (this.view === 'month') {
			if (this.month === 1) { this.month = 12; this.year--; } else this.month--;
		} else this.weekStart = frappe.datetime.add_days(this.weekStart, -7);
		this.load();
	},

	next() {
		if (this.view === 'month') {
			if (this.month === 12) { this.month = 1; this.year++; } else this.month++;
		} else this.weekStart = frappe.datetime.add_days(this.weekStart, 7);
		this.load();
	},

	setView(v) {
		this.view = v;
		document.querySelectorAll('.cal-viewbtn').forEach(b => b.classList.toggle('is-active', b.dataset.view === v));
		this.load();
	},
};

function make(wrapper) {
	wrapper.innerHTML = `
		<div class="cal-wrap">
			<div class="cal-head">
				<div>
					<div class="cal-title">${__("工作日历")}</div>
					<div class="cal-subtitle">${__('节假日 · 跟进提醒 · 出运计划 · 商机成交 · 工作检查')}</div>
				</div>
				<div class="cal-ctrl">
					<button class="btn btn-sm cal-prev">←</button>
					<button class="btn btn-sm cal-today">${__('今天')}</button>
					<button class="btn btn-sm cal-next">→</button>
					<span class="cal-views">
						<button class="btn btn-sm cal-viewbtn is-active" data-view="month">${__('月')}</button>
						<button class="btn btn-sm cal-viewbtn" data-view="week">${__('周')}</button>
					</span>
				</div>
			</div>
			<div class="cal-legend"></div>
			<div class="cal-main"><div class="cal-loading">${__('加载中…')}</div></div>
		</div>`;
	document.querySelector('.cal-wrap .cal-title').textContent = __('工作日历');

	CAL.init();
	CAL.load();
	wrapper.querySelector('.cal-prev').addEventListener('click', () => CAL.prev());
	wrapper.querySelector('.cal-next').addEventListener('click', () => CAL.next());
	wrapper.querySelector('.cal-today').addEventListener('click', () => { CAL.init(); CAL.load(); });
	wrapper.querySelectorAll('.cal-viewbtn').forEach(b => b.addEventListener('click', () => CAL.setView(b.dataset.view)));
}

frappe.pages['work-calendar'].on_page_load = function (wrapper) {
	make(wrapper);
};
