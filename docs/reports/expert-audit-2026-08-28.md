# 外贸ERP 售前全维度专家审计汇总（2026-08-28）

> 4 位专家并行只读审计：PM(需求完整度) / ARCH(架构数据) / DEV(代码按钮) / QA(实测矩阵)。
> 明细报告：/tmp/expert_pm.md(195行) /tmp/expert_arch.md(338行) /tmp/expert_dev.md(492行) /tmp/expert_qa.md(124行)
> 汇总规则：同一问题多专家命中=交叉确认，级别取最高。合计去重后：P0×8 / P1×16 / P2×25。

## 一、P0（售前演示会当场穿帮 / 核心功能不可用）— 8 条

| # | 问题 | 位置 | 交叉验证 | 修复建议 |
|---|---|---|---|---|
| P0-1 | 邮件群发"发送"必崩（AttributeError，doc.track 不存在） | bulk_email.py:63 + Bulk Email 缺 track/opened/clicked 字段 | PM+ARCH+DEV 三方命中 | DocType 补 3 字段，send_bulk_email 重写 |
| P0-2 | "报表中心"Workspace 是空壳（0 报表链接，只有 3 个空栏目） | workspace/报表中心.json content | PM | 重建 content 挂 18 报表链接 |
| P0-3 | IMAP 同步去重全废（Mail 无 message_id 列，exists 恒空→每5分钟重复拉全部邮件） | mail_sync.py:50,78 | ARCH+DEV 命中 | 迁移加 message_id+Unique 索引 |
| P0-4 | 客户合并功能必 500 且中途污染数据（SO 无 party_name 列；无事务回滚） | crm_utils.py merge_customers + customer_360.js:20(.wrap/.review_status) | ARCH+DEV 命中 | 改字段名+事务回滚+前端 .wrapper/approval_status |
| P0-5 | "下属邮件"按钮全角色 500（User 表无 department 列）+ 堆栈回显 | mail_ops.py:175 | DEV+QA 命中（QA 实测 6 角色全 500） | 改用自定义字段/Employee 关联+错误脱敏 |
| P0-6 | 单证打印 PI/CI/PL/BL 格式未入库（patch 未注册），红字卖点"单证一键打印"不可演示 | patches.txt + tabPrint Format 0 条 | PM | 注册 patch+migrate+smoke 加存在性检查 |
| P0-7 | 出运明细单与订单零联动（items 手工重录，需求 4.8 未兑现） | shipment.py 全文 pass | PM | 加"从订单生成"按钮+服务端拉 SO 明细 |
| P0-8 | 单证制作是空登记表（0 数据、无内容生成、只能手填贴附件） | trade_document.py | PM | 至少一键指向 Print Format 出 PDF |

## 二、P1（严重：安全越权 / 演示数据穿帮 / 核心流断点）— 16 条

### 安全类（SEC 视角，售前必须堵）
| # | 问题 | 证据 |
|---|---|---|
| P1-1 | 8 个邮件/线索/客户自定义方法（approve/distribute/file/archive/export/assign_lead/handover）**全部无角色校验**：采购/仓管/财务可审批销售邮件、可分派线索、可移交客户 | QA 按钮矩阵 44/48 格全 200 |
| P1-2 | get_mails 返回全员邮件，销售可见主管邮件；Mail/Mail Account 权限含 All 可写 | QA 实测+ARCH 权限审计 |
| P1-3 | export_mails 任何角色可导出全部邮件且 limit 无上限 | QA 实测 28 封全量 CSV |
| P1-4 | track_click 开放重定向（allow_guest+u 参数 302 任意域→钓鱼风险） | DEV 实测 302→example.com |
| P1-5 | 新建邮件 sender 前端传入可伪造 | DEV mail.py:12 |
| P1-6 | handover_customer 用 db_set 绕过 Customer 写权限（销售主管/仓管/老板都能改归属） | QA 实测 200 |
| P1-7 | 出运单状态可任意跳（sales1 草稿直改"已出运"成功，无 workflow 无校验） | QA 状态机实测 |
| P1-8 | 费用报销/采购审批的 4 条 transition 全 allowed=System Manager：业务审批人走不了流程，只有管理员能点 | QA 工作流实测 |

### 演示/数据链类
| # | 问题 | 说明 |
|---|---|---|
| P1-9 | 演示财务三口径对不上：SO 12万USD / 发票 80.6万CNY / 收款 25万CNY，无核销引用，应收虚高 | PM 发现，售前走单必穿帮 |
| P1-10 | 收款不走 against 发票核销，应收数字卡失真 | ARCH |
| P1-11 | 订单利润成本恒 0（SO Item valuation_rate 全 0）→ 毛利率 100% 假数据 | PM+ARCH |
| P1-12 | 工作台残缺：待办恒 0、今日汇率空白、两张趋势图不存在、销售额 KPI 混币种相加 | PM+DEV |
| P1-13 | 客户三级数据范围未落地（department 全空、User Permission 0 条）→"主管看下属客户/邮件"整体不成立 | PM+DEV（下属邮件 P0-5 同源） |
| P1-14 | 公海回收天数设置不生效（issingle=0 却用 get_single_value 读，实测返回 0） | PM 实测 |
| P1-15 | 采购链断点：验货不合格不拦入库（doc_events 整段被注释） | ARCH |
| P1-16 | 真实外发通道缺失：已发送文件夹是内部便签，SMTP 0 配置，"邮件"产品价值打对折 | ARCH（售前演示真实收发邮件需要 SMTP 演示方案） |

## 三、P2（一般：体验/观感/技术债）— 25 条（择要）

- 观感类：系统参数 name=hash、Workflow State 中英两套、getdoctype 空参报错、417 错误码+堆栈回显（建议统一 422+脱敏）、export CSV 无 BOM（Excel 乱码）
- 功能残缺：公海/热点/我的客户无 List View、商机三状态无视图、工作日历节假日恒空、"PI"子串误触发审批（"API"命中）、网站留言频控文案与实现不符
- 性能：get_mails N+1、员工工作情况表每用户 7 查询、全部自定义表 ~15 个查询列无索引
- 产品化债：6 张自定义单据无 company 字段（多公司扩展）、Shipment/Email Template 与 ERPNext 核心同名（表结构合并 67 列混排，升级高危）、erp_fixes 5 处 monkey-patch 无版本断言（升级即静默失效）、System Parameter 双轨（种子 5 条代码零读取）
- 角色配置：boss1 缺 Expense Reimbursement submit 权（老板不能提交报销）、salesm1/boss1 对 Customer 无 write
- 文档：business-flows.md 演示单清单与库不符（QC-2026-001 不存在）、库存预警口径文档不符

## 四、多维度交叉结论

**1. 权限模型（QA 双矩阵 + SEC 视角）**
- REST 资源端点（/api/resource）拦截完好：9/9 越权全 403，4/4 有权放行——**单据级 RBAC 是健康的**
- 但 /api/method 白名单自定义方法层**整体裸奔**（8/8 无校验）——这是 8 条安全 P1 的共同根因
- 修复策略：在 general_erp 加统一装饰器 require_roles([...]) 一次收口 8 个方法，而不是逐个打补丁

**2. 按钮级健康度（DEV+QA）**
- 实测 8 个自定义按钮：3 个必崩（下属邮件 500 / 客户合并 500 / 群发发送 500）、2 个无权限、1 个无 UI 入口（线索分发）、2 个正常（归档/建档）
- 其余标准 ERPNext 按钮（提交/审批/打印）经工作流实测可用
- 结论：自研按钮的"接线"完成度约 60%，售前演示路线要避开 3 个必崩按钮或先修

**3. 业务链完整度（ARCH）**
- 销售链：报价→订单→出库→发票 ✅ 通；收款核销 ❌ 断（P1-9/10）
- 采购链：订单(审批)→验货→入库 ✅ 通；验货→入库联动 ❌ 断（P1-15）
- 物流链：订单→出运→单证 ❌ 断两环（P0-7/8）
- 邮件链：内部流转 ✅；真实收发 ❌（P0-3/P1-16）
- 审批链：配置存在但 transition 全 System Manager ❌ 业务人走不通（P1-8）

**4. 报表口径（DATA 视角，PM+ARCH 命中）**
- 18 报表 100% 可运行（QA 回归 18/18）
- 口径分裂：docstatus 语义 3 种、币种 2 套、日期默认 3 种；订单利润成本恒 0、业绩排行按 owner 失真
- 修复优先级低于 P0/P1，但"订单利润 100% 毛利"在演示里显眼，建议随 P1-11 一起修

**5. 角色体系（PM 视角）**
- 6 角色分工矩阵整体合理（QA 权限矩阵验证）
- 3 个配置债：老板缺报销提交权、主管/老板缺客户写权、department/UP 未配（下属视角全空）

## 五、其他专家轻量意见（OPS/PO/PMO/DOC/SAST/MUT/DEL）

- **OPS**：IMAP 每 5 分钟重复拉取（P0-3）在客户生产环境会造成邮件表膨胀+重复提醒，属运维级风险；建议修复后加"同步去重"进 smoke。无索引 15 列（P2）在数据量 10 万级后报表会明显变慢，建议随 P0-3 迁移一次补。
- **PO**：售前 demo 路线建议重排——现在能漂亮演示的是：销售全链+采购审批+库存预警+18 报表+多角色权限；不能碰的 3 个雷：群发发送、客户合并、下属邮件。建议做一张"演示脚本卡"写进 docs/guide/。
- **PMO**：P0×8+P1×16 全修约 10-14 人日；建议两波：Wave1（售前阻塞）=P0 全部+P1 安全 8 条，5-6 天可交付演示版；Wave2（交付级）=P1 剩余+P2 高危（索引/核销/口径），5-8 天。
- **DOC**：business-flows.md 有 2 处与库不符（演示单清单、分发按钮），修复波次结束必须回改文档。
- **SAST**：本轮安全发现（越权×8、开放重定向、sender 伪造、堆栈回显）与 OWASP A01 越权/A03 注入无关但 A05 安全配置命中；修复后建议跑一次 semgrep 全 app 扫描收口。
- **MUT**：mail_tracking/审批状态机/merge_customers 是核心状态逻辑，修复后抽 mutation testing 验证用例杀伤力。
- **DEL**：交付前检查单缺口——/health 健康检查接口、HTTPS、发版前备份脚本、smoke.sh 均未建（产品化前置，与 productization-plan.md T3 同批）。

## 六、建议执行波次（待用户拍板）

**Wave 1 · 售前演示版（P0 全部 + 安全 P1，约 5-6 天）**
1. 邮件体系：Bulk Email 补字段+群发修复、Mail 补 message_id、下属邮件修列、get_mails 数据范围、export 权限+上限、track_click 白名单、sender 强制
2. 统一权限装饰器收口 8 方法（approve 限主管/审批角色、export 限财务+主管、assign_lead 限销售系、handover 加 write 校验）
3. 客户合并修字段+事务回滚、客户 360 修 .wrapper/approval_status
4. 报表中心 Workspace 重建挂 18 报表
5. 单证：注册打印 patch+出运"从订单生成"+Trade Document 一键出 PDF
6. 工作流 transition 改业务审批角色；老板补报销提交权
7. 演示数据链重建：口径自洽的销售→发票→收款核销链（USD/CNY 统一）

**Wave 2 · 交付级（P1 剩余 + P2 高危，约 5-8 天）**
8. 收款 against 核销、订单利润成本口径、采购验货联动启用
9. 公海回收参数生效、department+User Permission 配置（下属客户/邮件视角）
10. 15 列补索引、get_mails 去 N+1、错误码统一 422+脱敏
11. 公海/热点 List View、商机视图、趋势图 2 张、待办/汇率数字卡
12. business-flows.md 回改、演示脚本卡

**不修/延后（登记）**：多公司 company 字段、Shipment 改名去撞名（升级高危但当前版本锁定可延后）、monkey-patch 加固（升级前必做）、生产任务单定制、SMTP 真实收发（需客户提供邮箱）

