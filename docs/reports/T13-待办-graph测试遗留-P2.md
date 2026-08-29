# T13-待办-graph测试遗留 P2（2026-08-30）

来源：graph 全角度测试（报告 docs/reports/graph测试报告-2026-08-30.md）。均不阻断交付。

| 卡 | 状态 | 级别 | 问题 | 处置建议 |
|---|---|---|---|---|
| D1 | 待做 | P2 | sales1 等所有 desk 用户可看全量激活用户姓名+邮箱（Frappe 上游默认：Desk User 对 User 单据 select=1） | 生产交付前评估：Custom DocPerm 覆盖 User 单据 select=0（注意可能影响 desk "负责人"下拉渲染），或接受现状（基础通讯录） |
| D2 | 待做 | P2 | frappe serve 开发服务器 500 响应泄露 Python 堆栈+绝对路径 | 生产部署检查单必项：生产 WSGI（gunicorn/nginx）部署 + 确认响应无 exc 字段；本地演示环境可接受 |
| D3 | 已做(销项) | ~~P2~~误报 | 登录无失败锁定/限流 | 2026-08-30 复测：frappe 默认锁定生效（allow_consecutive_login_attempts=10，实测 11 连败后正确密码被拒"locked and will resume after 60 seconds"，清 redis login_failed_count/login_failed_time 解锁）。**注意**：锁定 key 是来源 IP 不是用户名，生产多人同 NAT 出口时一人连败会锁全公司，生产部署建议确认 lockout 粒度或 nginx 层按用户限流 |
| D4 | 待做 | P2 | 付款单并发双击败方返回 500 死锁报错（数据安全，仅报错不友好） | 体验优化：前端提交按钮防抖 + 后端捕获 Deadlock 重试/友好报错；优先级低 |

已完成（销项）：
- G5 site_config.json 权限 644→600（2026-08-30 已 chmod，bench 本地）
- G6 外销统计 N+1 → LEFT JOIN 预聚合（commit 084d4bd）
- G12 今日汇率 9 位小数 → 2 位（commit 084d4bd）

## 2026-08-30 第二轮 graph 复测
- 环境漂移检查：web 进程启动晚于 wave1 最后一次改动且期间无 .py 变更 → 无漂移，测试有效
- 回归 33/33 PASS；83 页全扫 0 真实问题（24 个 EMPTY? 均为已定性误报：报表类走 desk/报表名 错误 URL）
- D3 误报销项（见上表）；D1/D2/D4 维持待做
