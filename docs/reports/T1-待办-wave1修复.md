# T1 待办 · Wave1 售前演示版修复（状态：进行中）

> 来源：2026-08-28 四专家审计（docs/reports/expert-audit-2026-08-28.md）+ 用户拍板 Wave1 范围。
> 分支：general-erp/req-wave1-presale-fix。完成一条销一条（状态=已做+commit）。

## P0（售前阻塞）
| 卡号 | 事项 | 状态 | 验证标准 |
|---|---|---|---|
| W1-P0-1 | Bulk Email 补 track/opened/clicked 字段 + 修 send_bulk_email | 已做 | 群发送不崩，发出后状态流转正确 |
| W1-P0-2 | 报表中心 Workspace 挂 18 报表 | 已做 | get_workspaces content 22 块 + query_report.run 抽验 2 报表 200（2026-08-28） |
| W1-P0-3 | Mail 补 message_id 字段+Unique（迁移）+ 同步去重 | 已做 | 二次同步不产生重复 Mail |
| W1-P0-4 | 客户合并修 party_name→customer + 事务回滚；customer_360.js .wrap→.wrapper / review_status→approval_status | 已做 | merge 两客户走通且中途失败可回滚；360 页不崩 |
| W1-P0-5 | get_subordinate_mails 改列（department→自定义/Employee）+ API 错误脱敏 | 已做 | 6 角色调不再 500 |
| W1-P0-6 | 注册 create_trade_print_formats patch + migrate + 模板字段断链修复 | 已做 | tabPrint Format 出现 4 个单证格式，PI 可打印 |
| W1-P0-7 | Shipment 加"从订单生成"按钮+服务端拉 SO items | 已做 | 按钮生成后 items 与 SO 一致 |
| W1-P0-8 | Trade Document 一键出 PDF（指向 Print Format） | 已做 | 单证单据能出 PDF 文件 |

## P1 安全（8 方法收口）
| 卡号 | 事项 | 状态 | 验证标准 |
|---|---|---|---|
| W1-P1-1 | 新建 require_roles 装饰器；approve_mail→Sales Manager/System Manager；assign_lead→销售系；export_mails→财务/主管+limit 上限 5000 | 已做 | QA 按钮矩阵复测：非授权角色 403 |
| W1-P1-2 | get_mails 数据范围（本人 sender/recipient + 主管看本部门） | 已做 | sales1 看不到 salesm1 邮件 |
| W1-P1-3 | track_click 域名白名单 | 已做 | 302 目标仅限站内/白名单域 |
| W1-P1-4 | create_mail sender 强制 session.user | 已做 | 伪造 sender 参数无效 |
| W1-P1-5 | handover_customer 入口加 has_permission(Customer,write) | 已做 | 仓管/财务移交被拒 |
| W1-P1-6 | Shipment 状态流转校验（controller 矩阵或 workflow） | 已做 | 草稿直改已出运被拒 |
| W1-P1-7 | 工作流 transition 角色：采购订单审批→Purchase Manager/Sales Manager；费用报销审批→Accounts Manager/Sales Manager；老板补 Expense submit 权 | 已做 | 已落库验证：费用报销 草稿→审批中[Desk User] 审批/驳回[Accounts Manager,Sales Manager]；采购 提交[PU,PM] 审批/驳回[SM,PM]（2026-08-28 重跑 w1_wf3.py 多行 transition 模式） |
| W1-P1-8 | export_mails 权限+上限（并入 W1-P1-1） | 已做 | 任意角色全量导出被拒 |

## P1 演示数据
| 卡号 | 事项 | 状态 | 验证标准 |
|---|---|---|---|
| W1-P1-9 | 重建口径自洽演示链：SO(USD)→DN→SI(USD 开票)→PE 收款 against SI（CNY 按汇率核销），金额闭环 | 已做 | SO-1 12万USD→DN-3→SI-3(USD 12万/base 80.616万)→PE-5 收 25万 CNY 核销 SI；outstanding 556160+250000=806160 对账平（2026-08-28） |
| W1-P1-10 | 订单利润成本口径（SO Item valuation_rate 用 Item 成本价填充） | 已做 | Item 成本 800/220/3/5 USD；SO 行回填；订单利润报表 00001 率 33.33%、00005 率 37.14%（2026-08-28） |
| W1-P1-11 | 工作台：补 2 张趋势图（Dashboard Chart）、今日汇率数字卡种子、待办聚合、销售额币种统一 | 已做 | 新建销售订单趋势/采购订单趋势（Report 型，7-8 月有值）；今日汇率卡改指 Currency Exchange=6.718；3 条演示 ToDo；5 卡 4/38.2万/3/55.6万CNY/6.718 全有值（2026-08-28） |
| W1-P1-12 | department + User Permission 配置（销售部门+主管-下属 UP） | 已做 | 6 演示用户 erp_department 已设；sales1 UP 2 客户/ salesm1 UP 6 客户（含下属）；DBQuery 实测 sales1 见 2、salesm1 见 6；get_mails 主管含下属邮件（2026-08-28） |

## E2E 全流实测（expert_e2e2 执行中）
| 卡号 | 事项 | 状态 |
|---|---|---|
| W1-E2E | E1-E14 全业务流走通性报告 | 进行中 |

## 延后（Wave2+，只登记不修）
- 公海回收参数 issingle 修复 / 验货→入库联动 / 15 列索引 / get_mails N+1 / 422 脱敏 / List View 三缺 / 多公司 company 字段 / Shipment 改名去撞名 / monkey-patch 加固 / SMTP 真实收发 / 生产任务单定制

