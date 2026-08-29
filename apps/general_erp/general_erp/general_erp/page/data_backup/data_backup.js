// 数据与备份页面：备份列表 + 一键备份 + 下载

const BACKUP_PAGE = function(wrapper) {
	const el = document.createElement('div');
	el.className = 'data-backup-wrap';
	el.innerHTML = `
		<div class="db-header">
			<div class="db-title">数据与备份</div>
			<div class="db-sub">系统数据备份与恢复管理 · 建议每日自动备份一次</div>
		</div>
		<div class="db-actions">
			<button class="btn btn-primary db-backup-btn">
				<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/><path d="m16 5 4-4 4 4"/><path d="M18 2v8h8"/></svg>
				立即备份
			</button>
			<span class="db-status"></span>
		</div>
		<div class="db-table-wrap">
			<table class="db-table">
				<thead><tr><th>备份文件</th><th>时间</th><th>大小</th><th>操作</th></tr></thead>
				<tbody id="db-list"></tbody>
			</table>
		</div>
		<div class="db-tips">
			<h4>备份说明</h4>
			<ul>
				<li>备份包含全部数据库表结构 + 数据（不含附件文件）</li>
				<li>系统重装后，通过 bench restore 命令导入备份文件即可完整恢复</li>
				<li>建议每天备份一次，保留最近 14 天</li>
				<li>每日自动备份已配置（macOS launchd 定时任务）</li>
			</ul>
		</div>
	`;
	wrapper.append(el);

	const listEl = el.querySelector('#db-list');
	const statusEl = el.querySelector('.db-status');

	function refresh() {
		frappe.call({
			method: 'general_erp.general_erp.api_backup.get_backup_list',
			callback: (res) => {
				listEl.innerHTML = '';
				const files = res.message || [];
				if (!files.length) {
					listEl.innerHTML = '<tr><td colspan="4" style="text-align:center;color:#999">暂无备份，请先点击「立即备份」</td></tr>';
					return;
				}
				files.forEach(f => {
					const tr = document.createElement('tr');
					tr.innerHTML = `
						<td>${f.filename}</td>
						<td>${f.created}</td>
						<td>${f.size_mb} MB</td>
						<td><a class="db-dl btn btn-xs btn-secondary" data-name="${f.filename}">下载</a></td>
					`;
					listEl.appendChild(tr);
				});
				// 绑定下载
				listEl.querySelectorAll('.db-dl').forEach(a => {
					a.addEventListener('click', (e) => {
						e.preventDefault();
						window.open('/api/method/general_erp.general_erp.api_backup.download_backup?filename=' + encodeURIComponent(a.dataset.name), '_blank');
					});
				});
			}
		});
	}

	el.querySelector('.db-backup-btn').addEventListener('click', function() {
		this.disabled = true;
		this.textContent = '备份中...';
		statusEl.textContent = '正在备份数据库，请稍候...';
		frappe.call({
			method: 'general_erp.general_erp.api_backup.trigger_backup',
			callback: (res) => {
				this.disabled = false;
				this.innerHTML = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/><path d="m16 5 4-4 4 4"/><path d="M18 2v8h8"/></svg> 立即备份';
				const msg = res.message || {};
				statusEl.textContent = msg.message || '备份完成';
				if (msg.success) {
					statusEl.style.color = 'green';
					refresh();
				} else {
					statusEl.style.color = 'red';
				}
			},
			always: () => { this.disabled = false; }
		});
	});

	refresh();
};

// 内联样式
const style = document.createElement('style');
style.textContent = `
.data-backup-wrap{max-width:900px;margin:0 auto;padding:24px}
.db-header{margin-bottom:20px}
.db-title{font-size:22px;font-weight:600;color:var(--erp-text-1,#222)}
.db-sub{font-size:13px;color:var(--erp-text-3,#888);margin-top:4px}
.db-actions{display:flex;align-items:center;gap:12px;margin-bottom:20px}
.db-status{font-size:13px}
.db-table{width:100%;border-collapse:collapse}
.db-table th{text-align:left;padding:8px 12px;border-bottom:2px solid #eee;font-size:13px;color:#666}
.db-table td{padding:8px 12px;border-bottom:1px solid #f0f0f0;font-size:13px}
.db-table tr:hover td{background:#f9f9f9}
.db-tips{margin-top:24px;padding:16px;background:#f5f5f5;border-radius:8px}
.db-tips h4{font-size:14px;font-weight:600;margin:0 0 8px;color:#555}
.db-tips li{font-size:13px;color:#777;line-height:1.8}
`;
document.head.appendChild(style);

frappe.pages['data-backup'].on_page_load = function(wrapper) {
	BACKUP_PAGE(wrapper);
};
