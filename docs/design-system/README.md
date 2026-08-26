# 设计系统（Design System）— general-erp-web

> 本项目 UI/UX 规范。目标：让二开新增的单据表单、报表、看板、独立页面与 ERPNext 基座视觉统一，同时达到参考图（3 张 Dashboard 设计稿）的信息密度与品质感，术语与交互习惯对齐 Semi Design。

## 参考来源

1. **3 张 Dashboard 参考图**（Social Orbit / Apex / FinanceFlow 风格）：浅色底 + 白卡片 + 细边框、蓝色主色、KPI 卡（大数字 + 涨跌徽章）、线性图表、圆角图标磁贴、分组侧边导航（MAIN/OTHERS）、顶栏（搜索 ⌘K + 通知 + 语言 + 头像）。
2. **Semi Design（字节跳动）**：色彩中性灰阶、token 化命名、组件状态体系、文案与无障碍规范。

## 文档索引

| 文档 | 内容 |
|---|---|
| [01-design-tokens.md](01-design-tokens.md) | 设计变量：色彩、字体、间距、圆角、阴影、栅格布局 |
| [02-icons.md](02-icons.md) | 图标系统：尺寸、描边、命名、磁贴用法 |
| [03-components.md](03-components.md) | 组件系统：按钮、导航、卡片、表格、标签、弹窗、通知 |
| [04-forms.md](04-forms.md) | 表单系统：字段、校验、控件、布局密度 |
| [05-interaction.md](05-interaction.md) | 交互系统：反馈层级、状态机、键盘、错误处理 |
| [06-motion.md](06-motion.md) | 动效系统：时长、缓动、微交互、图表动效 |
| [07-data-viz.md](07-data-viz.md) | 图表与数据展示：KPI 卡、线/柱/环图、坐标轴、Tooltip |

## 落地方式（在 ERPNext 上怎么用这套规范）

所有自定义 UI **只进 `apps/general_erp/`**，通过以下挂载点生效（详见 `apps/general_erp/general_erp/hooks.py`）：

| 挂载点 | 用途 |
|---|---|
| `app_include_css` | 全站 CSS：定义 `--erp-*` 设计变量（色彩/间距/圆角/阴影），覆盖 frappe 主题变量 |
| `app_include_js` | 全局 JS：增强列表视图行高、KPI 卡渲染等 |
| Desk Theme（系统设置 → Desk 主题） | 主色/字体等官方可配项，优先用它，能少写 CSS 就少写 |
| 自定义 Workspace / 报表 / 仪表盘 | 按 07-data-viz.md 的图表与 KPI 规范编排 |
| Print Format | 单据打印版式（另按打印规范，不套用屏幕色彩） |

原则：

- **先 token 后样式**：新页面/组件一律引用 `--erp-*` 变量，不写死色值；
- **不 fork 官方组件源码**：用 CSS 变量覆盖 + 钩子扩展，升级基座不冲突；
- **信息密度优先**：ERP 是高频操作工具，紧凑模式（行高 40-48px、字号 13-14px）优先于展示型留白。
