/* 网站留言代码：官网嵌入表单（Web Form）+ 可复制的嵌入代码 */

function make(wrapper) {
	const site = location.protocol + '//' + location.host;
	const formUrl = `${site}/website-lead`;
	const width = 640, height = 520;
	const snippet = `<iframe src="${formUrl}" width="${width}" height="${height}" style="border:0;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,.06)" loading="lazy"></iframe>`;
	const snippetJs = `(function(){var f=document.createElement('iframe');f.src='${formUrl}';f.width='${width}';f.height='${height}';f.style='border:0;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,.06)';f.loading='lazy';document.getElementById('erp-lead-slot').appendChild(f);})();`;

	wrapper.innerHTML = `
		<div class="wlc-wrap">
			<div class="wlc-head">
				<div>
					<div class="wlc-title">${__('网站留言代码')}</div>
					<div class="wlc-subtitle">${__('把下方代码嵌入官网任意位置；访客提交询盘后自动生成「线索」（来源：网站留言），可在线索列表分发跟进。')}</div>
				</div>
			</div>
			<div class="wlc-grid">
				<div class="card wlc-preview">
					<div class="wlc-sec">${__('表单预览')}</div>
					<iframe class="wlc-frame" src="${formUrl}" title="${__('表单预览')}"></iframe>
				</div>
				<div class="wlc-codes">
					<div class="card">
						<div class="wlc-sec">${__('嵌入方式一：iframe 代码')} <button class="btn btn-sm wlc-copy" data-k="iframe">${__('复制')}</button></div>
						<pre class="wlc-pre" id="code-iframe"></pre>
					</div>
					<div class="card">
						<div class="wlc-sec">${__('嵌入方式二：JS 动态注入')} <button class="btn btn-sm wlc-copy" data-k="js">${__('复制')}</button></div>
						<pre class="wlc-pre" id="code-js"></pre>
					</div>
					<div class="card wlc-note">
						<div class="wlc-sec">${__('安全说明')}</div>
						<div class="wlc-note-body">${__('表单仅暴露提交入口（Web Form 发布页），不暴露任何列表查询接口；字段白名单固定（姓名/公司/邮箱/电话/留言），提交自动生成线索并标记来源。')}</div>
					</div>
				</div>
			</div>
		</div>`;

	document.getElementById('code-iframe').textContent = snippet;
	document.getElementById('code-js').textContent = '<div id="erp-lead-slot"></div>\n<script>\n' + snippetJs + '\n</script>';

	wrapper.querySelectorAll('.wlc-copy').forEach(btn => {
		btn.addEventListener('click', () => {
			const txt = btn.dataset.k === 'iframe' ? snippet : '<div id="erp-lead-slot"></div>\n<script>\n' + snippetJs + '\n</script>';
			(navigator.clipboard ? navigator.clipboard.writeText(txt) : Promise.reject()).then(
				() => frappe.show_alert({ indicator: 'green', message: __('已复制到剪贴板') }),
				() => frappe.msgprint(txt),
			);
		});
	});
}

frappe.pages['website-lead-code'].on_page_load = function (wrapper) {
	make(wrapper);
};
