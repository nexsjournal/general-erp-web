# 03 · 组件系统（Components）

> 覆盖：按钮、导航、卡片、表格、标签、弹窗、通知、Tabs/Segmented。表单单列 04-forms.md。

## 1. 按钮（Button）

| 类型 | 样式 | 使用 |
|---|---|---|
| Primary | 底 `--erp-primary` 白字 | 每屏**最多 1 个**主操作（提交/保存） |
| Secondary | 白底、1px `--erp-border-1`、`--erp-text-1` 字 | 主操作旁的第一顺位（保存并继续） |
| Tertiary/Text | 无边框、`--erp-text-2` 字、hover 底 `--erp-bg-hover` | 次要操作、行内操作 |
| Danger | 底 `--erp-error` 白字（或 text-danger 行内红字） | 删除、取消审批等不可逆操作 |

- 高度：36px（紧凑，表格/表单内，`--btn-height`）/ 44px（页面级）；内边距 14-18px；圆角 `--erp-radius`（8px，疏朗版）；
- 字号 14px/500；图标+文字间距 6px；
- 状态：hover（primary→hover 色 / secondary→边框加深）；active（active 色，scale 0.98）；disabled（50% 透明 + `--erp-text-disabled`）；loading（内嵌 spinner 替代图标，宽度锁定防跳动）；
- 按钮组顺序：主操作在右（中文习惯「取消 / 确定」左到右，确定在右）。

## 2. 导航（Navigation）

### 2.1 顶栏（Topbar）

- 高 56px，左：logo（28px）+ 站点/公司名；中：全局搜索框（320px，占位「搜索 ⌘K」）；右：通知铃铛（红点徽章）+ 语言 + 头像（28px 圆形，hover 下拉菜单）。
- 底部 1px 分割线 `--erp-border-light`。

### 2.2 Workspace 索引（首页）

- 见 02-icons §4；网格 6 列（窄屏 4/3 列），磁贴间距 24px。

### 2.3 模块内导航（左侧列表）

- 分组标题：12px `--erp-text-3`，组间距 16px（参考图 MAIN / OTHERS 式分组）；
- 导航项：高 44px，左图标 20px + 14px 文本；常态 `--erp-text-2`，hover 底 `--erp-bg-hover`，**选中**：底 `--erp-primary-lighter` + 文本 `--erp-primary` + 左 3px 圆角指示条；
- 角标（未读/数量）：12px 圆角 pill，`--erp-primary-light` 底蓝字；告警用 error 浅底。

## 3. 卡片（Card）

- 结构：`--erp-bg-card` 底 + 1px `--erp-border-1` + `--erp-radius-lg` + `--erp-shadow-1`；
- 内边距 24px（看板，疏朗版）/ 18px（列表型）；
- 卡头：标题 16px/500 + 右侧操作区（图标按钮或下拉），标题行高 24px，与内容间距 16px；
- 卡头可带 16px 图标（`--erp-text-3` 色，或模块主色）；
- **KPI 卡**（数据展示核心单元，详见 07）：
  - 上行：13px `--erp-text-3` 标签（可带 16px 图标/来源平台徽标）；
  - 中行：数字 28-32px/600 tabular-nums `--erp-text-1`（疏朗版基准 28px）；
  - 下行：涨跌徽章（见下）+ 「vs 上期」12px 说明；
  - 点击整卡可下钻（hover 边框变 `--erp-border-2` + `--erp-shadow-2`）。

### 涨跌徽章（Delta Badge）

- 12px 圆角 pill，内边距 2px 8px，12px/500 数字 + 箭头图标 12px；
- 好：`--erp-success-light` 底 / `--erp-success-text` 字（↑ 或 +x%）；差：error 浅底红字（↓ 或 -x%）。

## 4. 表格（Table / List View）

- 表头：高 40px，12px `--erp-text-3`，底 `--erp-bg-muted`，可排序列带 12px 排序图标（激活 `--erp-primary`）；
- 行：高 48px（常规，默认，`--list-row-height`）/ 40px（紧凑）；文本 13px `--erp-text-2`；
- 边框：行分隔 1px `--erp-border-light`（不要竖线）；hover `--erp-bg-hover`；选中底 `--erp-primary-lighter`；
- 数字列右对齐 + tabular-nums；金额带货币前缀；
- 状态列用标签（下节）；
- 空态：40px 线性图标 + 14px 说明 + 可选操作按钮，垂直居中；
- 加载：骨架屏（行高与真实行一致，3-5 行，微光扫过 1.2s 循环）；
- 分页：底栏「共 N 条 / 每页 20」+ 页码（当前页 primary 底白字）。

## 5. 标签 / 徽章（Tag / Badge）

- 高 20-24px，内边距 2-8px，圆角 4px，12px/500；
- 语义色映射（ERPNext 单据状态通用约定）：

| 状态 | 颜色 |
|---|---|
| 草稿 Draft | 灰（`--erp-bg-muted` 底 / `--erp-text-3` 字） |
| 提交/待处理 Submitted/Pending | 蓝（info 浅底） |
| 已批准/完成 Approved/Completed/Paid | 绿（success 浅底） |
| 逾期/拒绝 Overdue/Rejected/Cancelled | 红（error 浅底） |
| 临期/部分 Partial/Due Soon | 琥珀（warning 浅底） |

- 通知红点：8px 纯圆点 + 白描边（顶栏铃铛）；数字徽章 12px pill。

## 6. 弹窗 / 抽屉（Dialog / Drawer）

- 遮罩：`rgba(29,33,41,0.45)`；
- 弹窗：宽 480px（确认/小表单）/ 720px（表单），圆角 12px，`--erp-shadow-3`；结构 = 标题（16px/600，右上关闭 20px）+ 内容（16-24px 内边距）+ 底栏（右对齐按钮组，间距 8px，分隔线分隔底栏）；
- 抽屉：右侧滑出 480-560px，用于「查看明细/编辑详情」类长表单，保留列表上下文；
- 危险确认：标题带 20px error 图标，主按钮 Danger。

## 7. 通知（Toast / Notification）

- Toast：顶部居中，距顶 16px；结构 = 16px 状态图标 + 14px 文本（+ 可选操作链接）；
  - 成功/失败 3s 自动消失，警告/信息 5s；右上 16px 关闭；
  - 同屏堆叠上限 3，超出排队；
- 页面级横幅（login-error-banner 式）：表单卡片顶部，error 浅底 + 红字 + 16px 图标，仅表单级错误用。

## 8. Tabs / Segmented

- Tabs（页级切换）：下划线式，20px 容器高，选中 14px/500 `--erp-primary` + 2px 底条（宽随文字，200ms 滑移）；
- Segmented（卡内小范围切换，如参考图 Top Location / Age Range / Gender）：`--erp-bg-muted` 底圆角 8px 容器，选中项白底 + `--erp-shadow-1` + `--erp-text-1`，13px/500，切换 150ms；
- 同层级 Tabs 与 Segmented 不混用。

## 9. 页面底色与分型（2026-08 二轮）

- 原则：同一页面内**一种画布色**，分层靠边框/分割线，不靠底色硬切（对齐 NetSuite/Salesforce/Ant Design 风格）；
- **列表页**（`.frappe-list`）：整块白画布，与顶部工具栏连成一体；表头透明 + 1px 分割线（`--erp-border-1`），行分隔 `--erp-border-light`，行 hover `--erp-bg-hover`；禁止出现彩色底带（早期 `--erp-bg-page` 直铺列表区的做法已废弃）；
- **表单页**（`.form-page`）：整页白画布（表单/评论/活动区同底），右侧栏用 1px 左分割线分层（`.layout-side-section` border-left），不再白块+灰底拼贴；
- **Workspace / 数据面板**：保持灰底画布（`--erp-bg-page`）+ 白卡片，与列表/表单页区分场景；
- **首页文件夹磁贴**（如「会计」，`icon_type=Folder`）：官方渲染是浅灰底空盒 + 5px 微缩图标（视觉缺失），覆盖为 52px 蓝底（#0289f7，与其他 solid 磁贴同色）白文件夹图标，隐藏内部微缩网格；官方 `.folder-icon` 的 `!important` 底色用更高特异性 + `!important` 对抗；
- 实现：`public/css/erp_theme.bundle.css` 第 5 节（`:has()` 定位分型）；JS 侧 `erp_fixes.bundle.js` 补丁 `get_doc_title` 返回值走 `__()`（单例 DocType 右侧栏标题本地化）。
