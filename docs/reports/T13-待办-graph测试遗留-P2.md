# T13-待办-graph测试遗留 P2（2026-08-30）

来源：graph 全角度测试（报告 docs/reports/graph测试报告-2026-08-30.md）。均不阻断交付。

| 卡 | 状态 | 级别 | 问题 | 处置建议 |
|---|---|---|---|---|
| D1 | 待做 | P2 | sales1 等所有 desk 用户可看全量激活用户姓名+邮箱（Frappe 上游默认：Desk User 对 User 单据 select=1） | 生产交付前评估：Custom DocPerm 覆盖 User 单据 select=0（注意可能影响 desk "负责人"下拉渲染），或接受现状（基础通讯录） |
| D2 | 待做 | P2 | frappe serve 开发服务器 500 响应泄露 Python 堆栈+绝对路径 | 生产部署检查单必项：生产 WSGI（gunicorn/nginx）部署 + 确认响应无 exc 字段；本地演示环境可接受 |
| D3 | 待做 | P2 | 登录无失败锁定/限流 | 生产部署前：System Settings 启用 Login lockout（失败 N 次锁 M 分钟）或 nginx 层限流 |
| D4 | 待做 | P2 | 付款单并发双击败方返回 500 死锁报错（数据安全，仅报错不友好） | 体验优化：前端提交按钮防抖 + 后端捕获 Deadlock 重试/友好报错；优先级低 |

已完成（销项）：
- G5 site_config.json 权限 644→600（2026-08-30 已 chmod，bench 本地）
- G6 外销统计 N+1 → LEFT JOIN 预聚合（commit 084d4bd）
- G12 今日汇率 9 位小数 → 2 位（commit 084d4bd）

