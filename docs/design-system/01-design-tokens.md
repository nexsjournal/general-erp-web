# 01 · 设计变量（Design Tokens）

> 所有视觉属性的唯一事实来源。实现时以 CSS 变量承载（`--erp-*` 前缀，经 `app_include_css` 注入），任何组件禁止写死色值/尺寸。

## 1. 色彩

### 1.1 品牌色（Primary）

| Token | 值 | 用途 |
|---|---|---|
| `--erp-primary` | `#2563EB` | 主按钮、选中态、链接、图表主色 |
| `--erp-primary-hover` | `#1D4ED8` | hover |
| `--erp-primary-active` | `#1E40AF` | 按下 |
| `--erp-primary-light` | `#DBEAFE` | 选中行背景、标签底、图表面积 |
| `--erp-primary-lighter` | `#EFF6FF` | 大面积浅色底（tab 选中底、callout） |

### 1.2 中性色（Neutral，参考 Semi 灰阶）

| Token | 值 | 用途 |
|---|---|---|
| `--erp-text-1` | `#1D2129` | 主文本、标题、KPI 数字 |
| `--erp-text-2` | `#4E5969` | 正文、表单 label、表格内容 |
| `--erp-text-3` | `#86909C` | 次要说明、表头、占位符 |
| `--erp-text-disabled` | `#C9CDD4` | 禁用文本 |
| `--erp-bg-page` | `#F2F4F9` | 页面底（疏朗版：更浅冷灰，拉开与卡片对比） |
| `--erp-bg-card` | `#FFFFFF` | 卡片/面板底 |
| `--erp-bg-hover` | `#F2F3F5` | 行/项 hover |
| `--erp-bg-muted` | `#F7F8FA` | 次级区域底（表头、代码块） |
| `--erp-border-1` | `#E4E7EC` | 卡片边框、输入框边框（常态） |
| `--erp-border-2` | `#C9CDD4` | 输入框 hover、分割线加粗 |
| `--erp-border-light` | `#EDEFF2` | 分割线、列表分隔 |

### 1.3 功能色（Semantic）

| 语义 | 主色 | 浅底 | 文本/图标 | 使用 |
|---|---|---|---|---|
| 成功 Success | `#00B42A` | `#E8FFEA` | `#009A29` | 成功 toast、已支付、达标 |
| 警告 Warning | `#FF9F0A` | `#FFF3E0` | `#CC7A00` | 临期、待审批提醒 |
| 错误 Error | `#F53F3F` | `#FFECE8` | `#CB2634` | 校验失败、逾期、失败 toast |
| 信息 Info | `#2563EB` | `#E8F3FF` | `#1D4ED8` | 提示、进行中 |

规则：

- 功能色**只表达语义**，不用作装饰；一个界面同一时刻最多 1 个 error 色焦点（第一个校验失败字段）。
- 涨跌徽章：财务语境按「好坏」而非「方向」着色——收入/利润涨=绿、跌=红；成本/费用涨=红、跌=绿。
- 对比度：正文对底 ≥ 4.5:1（WCAG AA）；大字号（≥24px）≥ 3:1。

### 1.4 图表色序（Chart Palette）

按顺序取色，超过 6 类合并为「其他」：

| # | 值 | 备注 |
|---|---|---|
| 1 | `#2563EB` | 蓝（主系列） |
| 2 | `#4CC3FA` | 浅蓝 |
| 3 | `#6B61FF` | 紫 |
| 4 | `#00B3A1` | 青 |
| 5 | `#F7BA1E` | 琥珀 |
| 6 | `#E94560` | 玫红 |
| 7 | `#818A9B` | 灰（「其他」固定用灰） |

约束：相邻两色不得同色系；红（#F53F3F）绿（#00B42A）只用于语义标注，不进入图表色序首位（色盲可辨）。

## 2. 字体（Typography）

### 2.1 字体栈

```css
--erp-font-family:
  Inter, -apple-system, "Segoe UI", Roboto,
  "PingFang SC", "Microsoft YaHei", "Noto Sans SC",
  sans-serif;
--erp-font-family-mono:
  "SF Mono", "JetBrains Mono", Consolas, monospace;
```

- 数字（KPI、金额、数量）用 `font-variant-numeric: tabular-nums` 保证等宽对齐。
- 代码/单号/条码内容用 mono。

### 2.2 字号阶梯

| Token | 值 | 行高 | 字重 | 用途 |
|---|---|---|---|---|
| `--erp-text-xs` | 12px | 16px | 400 | 徽章、时间戳、图表坐标 |
| `--erp-text-sm` | 13px | 20px | 400 | 表格内容（ERP 信息密度主力字号） |
| `--erp-text-base` | 14px | 22px | 400 | 正文、表单 label、按钮 |
| `--erp-text-md` | 16px | 24px | 500 | 卡片标题、小节标题 |
| `--erp-text-lg` | 20px | 28px | 600 | 页面标题 |
| `--erp-text-xl` | 24px | 32px | 600 | KPI 数字（常规） |
| `--erp-text-2xl` | 32px | 40px | 600 | KPI 数字（强调） |

- 字重只用 400 / 500 / 600 三档；不用斜体表达状态。
- 行标题层级用「字号 + 颜色深浅」区分，不用下划线/全大写。

## 3. 间距（Spacing）

4px 基础栅格：

| Token | 值 | 典型用途 |
|---|---|---|
| `--erp-space-1` | 4px | 图标与文字、徽章内边距 |
| `--erp-space-2` | 8px | 紧凑元素间距、表单组内 |
| `--erp-space-3` | 12px | 表单字段间距 |
| `--erp-space-4` | 16px | 卡片内边距（紧凑）、列表行内 |
| `--erp-space-5` | 24px | 卡片内边距（常规）、卡片之间 |
| `--erp-space-6` | 32px | 区块之间 |
| `--erp-space-8` | 48px | 页面级分隔 |

规则：同一容器内相邻元素间距取档不插值；卡片之间恒 16px（密集看板）或 24px（疏朗首页），不混用。

## 4. 圆角（Radius）

| Token | 值 | 用途 |
|---|---|---|
| `--erp-radius-sm` | 4px | 徽章、chip |
| `--erp-radius` | 6px | 按钮、输入框、下拉 |
| `--erp-radius-lg` | 16px | 卡片（疏朗版） |
| `--erp-radius-xl` | 20px | 图标磁贴、弹窗（疏朗版） |
| `--erp-radius-full` | 999px | 胶囊按钮、头像 |

## 5. 阴影（Shadow）

参考图以「细边框 + 极浅阴影」为主，不滥用投影：

| Token | 值 | 用途 |
|---|---|---|
| `--erp-shadow-1` | `0 1px 2px rgba(29,33,41,0.05)` | 卡片常态（配合 1px 边框） |
| `--erp-shadow-2` | `0 6px 16px rgba(29,33,41,0.07)` | 卡片 hover、浮动层 |
| `--erp-shadow-3` | `0 12px 32px rgba(29,33,41,0.10)` | 弹窗、下拉、抽屉 |

规则：阴影只用于「层级上浮」，不用阴影区分内容块（内容块用边框）。

## 6. 布局栅格（Layout）

| 项 | 值 |
|---|---|
| 顶栏高度 | 56px，`--erp-bg-card` 底 + 底部 1px `--erp-border-light` |
| 内容区 | 左右 padding 32px（≥1440px）/ 24px（<1440px）；max-width 不限（表格可满宽） |
| 看板网格 | workspace 栅格 gap 20px（疏朗版）；KPI 行 4 列（窄屏 2 列）；图表区 3:2 或 2:1 分栏 |
| 列表行高 | 48px（常规，默认）/ 40px（紧凑，超高密度场景显式指定） |
| 表单 label | 置于输入框上方（不做左侧 label 两栏，ERP 单据列多时纵向更稳） |

## 7. 暗色模式（预留）

- Token 命名按「语义 + 状态」组织，暗色模式仅换 token 值不改结构；
- 暗色底：页面 `#17181C`、卡片 `#1F2024`、边框 `#2E3035`；
- 暗色下阴影改为「亮边」：`0 0 0 1px rgba(255,255,255,0.04)` 内描边 + 更浅投影。
