# T2 待办 · Wave2 遗留 + 注意点全修（状态：✅ 全部完成）

> 来源：2026-08-28 用户拍板"全部修复"。分支：general-erp/req-wave1-presale-fix（改动留工作区，未提交）。
> 完成时间：2026-08-28。回归：18/18 报表 OK + 权限矩阵 8 组全绿 + 验货→入库 e2e 三场景 PASS + SO→出运单 e2e PASS。

## 修复项（全部销项）
| 卡号 | 事项 | 状态 | 验证结果 |
|---|---|---|---|
| T2-01 | 库存预警 LEFT JOIN | ✅ | 零库存+safety_stock item 进报表 |
| T2-02 | 商机默认值 | ✅ | opportunity_from=Customer / type=Sales 入库 |
| T2-03 | sales1 建 SI | ✅ | CDP 全量拷贝语义修复后 C=1 S=1 |
| T2-04 | 验货→入库联动 | ✅ | 合格→PR 生成 / 不合格→退货待办 / 不合格拦截PR，三场景 e2e PASS；修了 ToDo 无 subject 字段（标题并入 description）、exception_handling 默认"无"判定 |
| T2-05 | 公海参数生效 | ✅ | get_sys_param 统一读取 |
| T2-06 | 15 列补索引 | ✅ | SHOW INDEX 确认 |
| T2-07 | get_mails 去 N+1 | ✅ | 批量查 User |
| T2-08 | 422 脱敏 | ✅ | ValidationError http_status_code=422 验证 |
| T2-09 | 客户三视图 | ✅ | 我的/公海/热点 List Filter 入库 |
| T2-10 | 多公司 company 字段 | ✅ | 7 张自定义单据加 company Link（site_setup 幂等同步） |
| T2-11 | Shipment 改名去撞名 | ✅ | 整体改名 Export Shipment/Export Shipment Item：独立表 tabExport Shipment，ERPNext Stock Shipment 独立恢复（56 字段空表），3 行演示数据完好，报表/日历/单证/workspace/打印全部改指向 |
| T2-12 | monkey-patch 版本断言 | ✅ | app __init__ frappe 16.x 断言 + 422 补丁 |
| T2-13 | SMTP | ✅(占位) | demo-smtp 占位账号；真实 SMTP 需客户提供邮箱；未配置时群发记"部分失败"=预期行为（已确认不改） |
| T2-14 | 生产任务单审批 | ✅ | Production Plan 审批 workflow（草稿→审批中→已审批/已驳回）+ Manufacturing Manager 权限（write/submit） |
| T2-15 | 节假日数据 | ✅ | Holiday List 中国法定节假日-2026 + company 默认 |
| T2-16 | 参数名可读化 | ✅ | 5 条 hash→param_key |
| T2-17 | Workflow State 中英统一 | ✅ | 英文状态已删，全中文 |
| T2-18 | 留言频控 | ✅ | IP 每小时 5 条 Redis 计数 + 文案对齐 |
| T2-19 | System Parameter 统一 | ✅ | 公海参数 hash→param_key + get_pool_days 回退 |
| T2-20 | 员工表去 N+1 | ✅ | 单条批量 SQL，报表 OK |
| T2-21 | boss1 报销 submit / salesm1 客户 write | ✅ | CDP 全量拷贝语义（setup_custom_perms+add_permission），不塌 base 权限 |
| T2-22 | CSV BOM + 商机三视图 | ✅ | 商机三状态 List Filter（待批复/已批复/待回复） |

## 技术要点（防复发）
1. **frappe CDP 语义**：本 build 的 Custom DocPerm 是【整体替换】base DocPerm（meta.py set_custom_permissions），不是合并。改权限必须 setup_custom_perms（全量拷贝 base）→ 再改行/add_permission 补新角色行，禁止直接 insert 单条 CDP（会塌掉其他角色权限）。
2. **frappe 无内置 DocType 重命名工具**（rename_doc 对 doctype 只改 DocType 行+引用，不迁移表；且 base 字段归属按 parent 全量迁移会把两个同名 doctype 的字段混掉）。本项目的 Shipment 撞名处理=手工：DocType 行改名 + DocField/DocPerm 引用迁移 + RENAME TABLE + DBTable 重建对端表 + app 目录/类名同步。表名由 doctype 名推导（tab{DocType}）。
3. **frappe 会回写 app 目录的 doctype json/py**（insert/save 时），erpnext 仓库的文件被回写污染时必须 git checkout 还原（纪律：不改 frappe/erpnext 源码）。
4. 本 build ToDo 无 subject 字段（标题=description）。
5. Inspection Order 必须 is_submittable=1（on_submit/docstatus 依赖）；inspector=Link→User。
