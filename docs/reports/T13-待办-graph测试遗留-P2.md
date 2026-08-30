# T13-待办-graph测试遗留 P2（2026-08-30）

来源：graph 全角度测试（报告 docs/reports/graph测试报告-2026-08-30.md）。均不阻断交付。

| 卡 | 状态 | 级别 | 问题 | 处置建议 |
|---|---|---|---|---|
| D1 | 已做(销项) | P2 | sales1 等所有 desk 用户可看全量激活用户姓名+邮箱（Frappe 上游默认：Desk User 对 User 单据 select=1） | **2026-08-30 用户拍板收紧，已实施**：①Custom DocPerm 收回 Desk User 对 User 的 read/select——普通用户用户列表页只看到自己（浏览器实测 sales1=1 行，截图 d1_sales1_self.png）②新建「流程设计」角色（User read+select、Workflow/Module Flow 读写）授予 boss1+salesm1——流程设计者与管理员可见全员可维护流程 ③超管 System Manager 原生全权不受影响 ④普通用户仍可改自己资料/密码（自己详情页可开），读他人详情 403 ⑤site_setup.sync_user_privacy 幂等固化（连跑3次不产生重复 CDP，_cdp 改存在则更新）⑥回归 33/33 全绿 |
| D2 | 待做 | P2 | frappe serve 开发服务器 500 响应泄露 Python 堆栈+绝对路径 | 生产部署检查单必项：生产 WSGI（gunicorn/nginx）部署 + 确认响应无 exc 字段；本地演示环境可接受 |
| D3 | 已做(销项) | ~~P2~~误报 | 登录无失败锁定/限流 | 2026-08-30 复测：frappe 默认锁定生效（allow_consecutive_login_attempts=10，实测 11 连败后正确密码被拒"locked and will resume after 60 seconds"，清 redis login_failed_count/login_failed_time 解锁）。**注意**：锁定 key 是来源 IP 不是用户名，生产多人同 NAT 出口时一人连败会锁全公司，生产部署建议确认 lockout 粒度或 nginx 层按用户限流 |
| D4 | 待做 | P2 | 付款单并发双击败方返回 500 死锁报错（数据安全，仅报错不友好） | 体验优化：前端提交按钮防抖 + 后端捕获 Deadlock 重试/友好报错；优先级低 |
| D5 | 待做 | P2 | 已提交单据重复 submit 静默返回 200（v16 无守卫，语义误导） | 状态机类单据加 validate 已提交提示；低优先 |
| D6 | 待做 | P2 | PO 详情页工具栏缺"打印/提交"独立入口（藏在列表行操作菜单） | 详情表单加 actions；低优先 |
| D7 | 待做 | P2 | headless 下列表"新建"按钮 hover 显隐导致自动化卡住（真人可见，非产品缺陷） | 自动化改用 API/显式触发；非交付阻塞 |

已完成（销项）：
- G5 site_config.json 权限 644→600（2026-08-30 已 chmod，bench 本地）
- G6 外销统计 N+1 → LEFT JOIN 预聚合（commit 084d4bd）
- G12 今日汇率 9 位小数 → 2 位（commit 084d4bd）

## 2026-08-30 第二轮 graph 复测
- 环境漂移检查：web 进程启动晚于 wave1 最后一次改动且期间无 .py 变更 → 无漂移，测试有效
- 回归 33/33 PASS；83 页全扫 0 真实问题（24 个 EMPTY? 均为已定性误报：报表类走 desk/报表名 错误 URL）
- D3 误报销项（见上表）；D1/D2/D4 维持待做
## 2026-08-30 D1 权限收紧验证矩阵
| 场景 | 预期 | 实测 |
|---|---|---|
| sales1 打开 /desk/User 列表 | 只见自己 | ✓ 1 行（张伟 sales1@demo.com） |
| sales1 打开自己用户详情 | 可看可改（含改自己密码） | ✓ |
| sales1 打开 boss1 用户详情 | 拦截 | ✓ 无"刘老板"数据 |
| boss1（流程设计）打开 /desk/User | 全量 | ✓ 7 行 |
| boss1 打开 /desk/Module Flow | 可读可改 | ✓ 12 条 |
| sales1 打开 /desk/Module Flow | 拦截 | ✓ 无权限 |
| 回归 33 项 | 全绿 | ✓ 33/33 |

## 2026-08-30 第三轮 graph 测试（采购/库存/委外 + 财务/生产 + 产品/客户/邮件/报表）

**两个 P1 已修复（commit a3de050，守卫 tests/regression/test_approval_guard.py 5 用例固化回归）**

| P1 | 根因 | 修复 |
|---|---|---|
| 生产任务单"审批中"时提交人直接 Submit → 绕过 boss 审批（docstatus=1+状态"已审批"） | frappe v16：工作流"审批中"映射 doc_status=0，原生 Submit 置 docstatus=1 后 set_workflow_state_on_action 按 doc_status=1 匹配到"已审批"状态自动跳转；提交人"提交审批"动作留有 Workflow Action 记录不能作放行依据 | general_erp.approval_guard.guard_before_submit：审批中间态+无中间态 Workflow Action 留痕+无下一跳允许角色 → 拒绝；guard_before_save 覆盖 API 直改字段路径 |
| "审批中"采购订单可生成收货单并 submit 真实过账库存 | 收货链路只查 docstatus 不查 workflow_state | guard_purchase_receipt（validate）：源 PO 非"已审批" → 拒绝 |

验证：6 项守卫用例（提交人 submit 拒/审批人 submit 放行/直改状态拒/审批中 PO 收货拒/已审批 PO 收货放行/草稿 PO 原生 submit 不受影响）全过；全量回归 38/38 PASS；测试数据全清理（TEST- 前缀零残留，ITM-004 库存回基线 360）。

**本轮各模块结论（0 P0 / 2 P1 已修 / 5 P2 见上表 D5-D7 + T13 既有 D2/D4）**
- 采购/库存/委外（测试员A）：采购链 1500 元逐环一致、库存 +5 守恒、超卖 NegativeStockError 拒、预警报表出数；stock1 无委外权时"没有权限"提示不崩溃
- 财务/生产（测试员B）：报销审批流正确、收款 1000 元 GL 正确、3 原生报表带 FY2026 有数、3 统计报表出数；生产主链（任务单→工单→领料→入库）库存守恒 WIP 归零
- 产品/客户/邮件/报表（C 路 headless 卡住，主 agent API 补测 7 链全通）：商品 CRUD+无海关编码传统产品可建、商品组/海关编码 CRUD、客户+联系人+跟进、线索→商机转化、邮件记录/模板 CRUD、外销/收款/库存预警/产品统计+财务三表出数
- 越权/安全（tester_security）：27/31 硬过 0 放行，注入 7/7 安全（D2 堆栈泄露维持待做=生产部署必关）
- 数据流（tester_data）：金额守恒/幂等双提交/状态机非法流转拦截/并发 P95=91ms 零错误/数据隔离 403（D4 死锁 500 维持待做）
