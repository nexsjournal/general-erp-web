# 外贸 ERP 全功能与业务流程清单（交付版）

> 生成日期 2026-08-28（同日 Wave1 售前修复后刷新）。依据：需求清单图（docs/feature-requirements.md）+ 代码实测（18 报表全量跑通、6 角色权限实测、HTTP 越权验证、演示数据链闭环核验）。
> 状态标记：✅ 已实现并实测 / ⚠️ 已实现但有注意点 / ➖ 未实现（登记任务）。

## 一、功能模块清单（对照需求图）

### 1. 工作台
| 功能 | 状态 | 说明 |
|---|---|---|
| 待处理任务 | ✅ | ToDo 列表 + 工作台数字卡 |
| 通知公告 | ✅ | 公告 DocType + 工作台入口 |
| 今日汇率 | ✅ | 币种汇率 DocType + 数字卡 |
| 日历 | ✅ | 工作日历 page（work_calendar） |
| 工作检查 / 员工工作情况表 | ✅ | Work Check + 子表，周检流程 |
| 公司业务数据 | ✅ | 工作台数字卡（订单/销售额/应收/待办）+ 双趋势图 |
| 员工业绩排行榜 | ✅ | 报表（客户跟进数+成交单+金额排行） |

### 2. 线索
| 功能 | 状态 | 说明 |
|---|---|---|
| 线索管理 | ✅ | Lead + 状态流 Lead→Open→Replied→Opportunity→Quotation→… |
| 分发跟踪 | ✅ | 线索"分发"按钮 → Lead Distribution Log 留痕 |
| 线索统计 | ✅ | 报表 |
| 网站留言代码 | ✅ | website_lead_code page（嵌入代码生成） |

### 3. 邮件（红字重点区）
| 功能 | 状态 | 说明 |
|---|---|---|
| 待处理/收件箱/已发送/草稿箱/已删除 | ✅ | 邮件中心 page 五文件夹 |
| 待审批邮件 | ✅ | status=待审批 + 审批规则自动命中 |
| 邮件分发 | ✅ | 分发给下属，留痕 |
| 建档到客户 | ✅ | file_mail_to_customer |
| 归档 / 恢复 | ✅ | archive_mail + restore 字段 |
| 发送跟踪 | ✅ | 打开像素 + 点击跳转，opened/clicked 字段 |
| 导入 / 导出 | ✅ | CSV 导出（export_mails 实测返回文件 URL） |
| 下属邮件 | ✅ | get_subordinate_mails |
| 邮箱账号设置 | ✅ | Mail Account（IMAP 接入） |
| 邮箱设置/频率限制 | ✅ | 营销账号日发送上限/单收件人上限（Statistics Settings） |

### 4. 客户
| 功能 | 状态 | 说明 |
|---|---|---|
| 我的/下属/公海/全部/热点客户 | ✅ | 列表视图 + 公海回收天数参数（30 天） |
| 客户跟进一览 | ✅ | Customer Follow Up（电话/邮件/微信/拜访+下次跟进） |
| 客户 360 | ✅ | customer_360 page（跟进/商机/报价/订单/邮件聚合） |
| 移交 | ✅ | 客户"移交"按钮 + 留痕 |
| 合并 / 共享 / 修改历史 | ✅ | 官方能力（merged_into / 权限 / Version） |
| 导入 / 导出 / 回收站 | ✅ | 官方 Data Import / Export / 软删除 |
| 客户分析 | ✅ | 报表（按区域/行业等维度） |

### 5. 营销
| 功能 | 状态 | 说明 |
|---|---|---|
| 群发邮件 | ✅ | Bulk Email + 子表收件人 |
| 效果分析 | ✅ | success_count/total_count + 邮件统计报表群发成功率 |
| 营销账号设置 | ✅ | Mail Account + 频率限制 |
| 营销主题设置 | ✅ | Email Template |

### 6. 商机
| 功能 | 状态 | 说明 |
|---|---|---|
| 全部/待批复/已批复/待回复 | ✅ | Opportunity + approval_status 批复流 |
| 新评论 | ✅ | Communication 评论 |
| 商机统计 | ✅ | 报表（按批复状态：数量/金额/赢单率） |

### 7. 产品
| 功能 | 状态 | 说明 |
|---|---|---|
| 产品库（导入/导出/回收站） | ✅ | Item + Data Import/Export/软删除 |
| 感兴趣分析 / 报价分析 | ✅ | 两个报表（报价转化漏斗） |
| 产品属性维护 / 自定义属性 | ✅ | Item 属性 + Custom Field |

### 8. 销售管理
| 功能 | 状态 | 说明 |
|---|---|---|
| 报价管理 | ✅ | Quotation（有效期参数 30 天） |
| 外销订单 | ✅ | Sales Order（USD 外币） |
| 出运明细单 🔴 | ✅ | Shipment + Shipment Item（港口/船名/柜号/提单号/ETD/ETA/状态流） |
| 单证制作 🔴 | ✅ | Trade Document DocType |

### 9. 采购（🔴 整行 P0）
| 功能 | 状态 | 说明 |
|---|---|---|
| 供应商 | ✅ | Supplier |
| 采购订单 | ✅ | Purchase Order + 采购订单审批工作流 |
| 验货单 🔴 | ✅ | Inspection Order + Inspection Item |

### 10. 生产
| 功能 | 状态 | 说明 |
|---|---|---|
| 生产任务单 | ⚠️ | 复用 ERPNext Production Plan（未做定制审批流，见待办 T1） |

### 11. 财务（🔴 整行 P0）
| 功能 | 状态 | 说明 |
|---|---|---|
| 收款管理 | ✅ | Payment Entry(Receive)，收款统计报表（已修 SQL bug） |
| 付款管理 | ✅ | Payment Entry(Pay)，付款统计报表（已修 SQL bug） |
| 费用管理 | ✅ | Expense Reimbursement + 费用报销审批工作流（8 类费用） |
| 发票管理 | ✅ | Sales Invoice |
| 订单利润 | ✅ | 报表（收入-成本-费用，按已提交订单） |

### 12. 库存管理（🔴 整行 P0）
| 功能 | 状态 | 说明 |
|---|---|---|
| 入库 | ✅ | Purchase Receipt（实测提交过账） |
| 出库 | ✅ | Delivery Note（实测提交过账） |
| 库存余额 / 库存流水 | ✅ | Bin / Stock Ledger Entry |
| 仓管设置 | ✅ | Stock Manager 角色 + 仓库 |
| 库存预警 | ✅ | 报表（已修 safety_stock 字段引用 bug） |

### 13. OA
| 功能 | 状态 | 说明 |
|---|---|---|
| 文件管理 | ✅ | File DocType（系统级文件管理） |

### 14. 统计（🔴 各类报表起 P0）
18 个报表全部实测 OK：邮件/客户/统计设置（报表订阅+可见角色）/外销/收款/付款/采购/费用/产品/出运/库存预警/线索/商机/订单利润/报价/感兴趣/员工业绩/员工工作情况。

### 15. 设置
员工/部门/岗位与权限（RBAC 六角色）✅、基数数据（港口/贸易术语/HS/系统参数）✅、登录日志（Login Log）✅、订单条款（Terms and Conditions，工作台"设置"卡片入口）✅、系统参数✅、中英文配置（语言选择器+翻译）✅、海关商品（HS Code+申报要素）✅、区域设置（regional_settings page）✅、服务商✅、审核设置（工作流+审批规则）✅、企业信息（Company）✅、用户参数✅。

## 二、核心业务流程（端到端）

### F1 获客与线索流
网站留言/手动录入 → Lead（状态流：Lead→Open→Replied→Opportunity→Quotation→Converted/Lost）→ 主管"分发"给销售（留痕 Lead Distribution Log）→ 转化为客户 → 未跟进 30 天自动回公海 → 重新认领/回收。

### F2 销售报价成交流
客户/线索 → Quotation（30 天有效期）→ 客户确认 → Sales Order（提交=锁定，状态 To Deliver and Bill）→ Delivery Note 出库（过账，扣库存）→ Sales Invoice 开票 → Payment Entry(Receive) 收款核销。

### F3 出运物流流（P0）
Sales Order → Shipment（装运明细：商品行 + 起运港/目的港 + 贸易术语 + 船名航次 + 柜号 + 提单号 + ETD/ETA）→ 状态流：草稿→已订舱→已出运→已清关→已交付 → Trade Document 单证（报关/提单等附件）→ 出运统计报表。

### F4 采购验货流（P0）
Supplier → Purchase Order（**采购订单审批工作流**：提交→审批→驳回/通过）→ 到货 → Inspection Order 验货（逐行检验项+结果）→ Purchase Receipt 入库（过账，加库存）→ Payment Entry(Pay) 付款。

### F5 费用审批流（P0）
Employee 发起 Expense Reimbursement（8 类费用，可挂订单/项目）→ **费用报销审批工作流** → 提交(docstatus=1) → 费用统计/订单利润报表归集。

### F6 邮件营销与合规流
Email Template 主题 → Bulk Email 群发（营销账号频率限制：日上限/单收件人上限）→ 发出件审批（审批规则自动命中→待审批文件夹→人工批准/驳回）→ 发送跟踪（打开/点击时间戳）→ 效果分析（群发成功率+打开率）→ 建档到客户/分发/归档。

### F7 库存流（P0）
入库：采购收货单过账 / 出库：销售出库单过账 → Bin 实时余额 → 低于安全水位 → 库存预警报表（缺口=安全水位-预计量）→ 补货（走 F4）。

### F8 绩效与统计流
各业务单据 → 18 报表（默认本月区间，可改）→ 报表订阅（定时推送，Statistics Settings）→ 报表可见角色控制（Report Role）→ 员工业绩排行（客户维度：跟进数+成交单+金额）。

### F9 权限与角色流
RBAC：张销售(Sales User) / 李销售主管(Sales Manager) / 王采购(Purchase Manager) / 赵仓管(Stock Manager) / 陈财务(Accounts Manager) / 刘老板(全角色)。
已实测：每角色菜单/单据可见性 + HTTP 越权访问全部 403 拦截；系统参数等设置类全员只读。

### F10 演示数据链（售前演示口径自洽，2026-08-28 重建）
| 单据 | 名称 | 金额 | 关联 |
|---|---|---|---|
| 汇率 | Currency Exchange 2026-08-28 | USD→CNY 6.718 | Accounts Settings 多币种开票开关=开 |
| 销售订单 | SAL-ORD-2026-00001（深圳星辰科技） | USD 120,000 | Completed，delivered 100% / billed 100% |
| 出库单 | MAT-DN-2026-00003 | USD 120,000 | against_sales_order→SO-1，Completed |
| 发票 | ACC-SINV-2026-00003 | USD 120,000 / CNY 806,160 | 源单→DN-3→SO-1，Partly Paid |
| 收款 | ACC-PAY-2026-00005 | CNY 250,000（T/T 2026-08-15） | 核销 SI-3，outstanding=556,160，556,160+250,000=806,160 对账平 |

成本口径：Item valuation_rate（USD 成本：笔记本 800 / 手机 220 / T恤 3 / 耳机 5），SO Item 已回填 → 订单利润报表毛利率 33.33% / 37.14%（非 100%）。

客户归属：sales1 名下 深圳星辰科技/上海远航；salesm1 名下 汉堡/Tokyo/Dubai/New York（sales_owner + User Permission：sales1 见 2 客户、salesm1 见 6 客户（含下属）；邮件 get_mails 主管含下属、销售仅本人+被分发）。

## 三、遗留与待办
| 编号 | 事项 | 级别 |
|---|---|---|
| T1 | 生产任务单仅复用 ERPNext Production Plan，无定制审批流/字段，若客户要求"生产任务单"定制字段需补 DocType | P2 |
| T2 | 品牌资产（产品名/Logo/Favicon）待用户提供后落地 | P2（产品化前置） |
| T3 | 法律层：AGPL 基座合规策略需用户拍板（见 productization-plan.md） | P0（售前必须） |

