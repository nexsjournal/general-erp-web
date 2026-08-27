# 夜间模式（Dark Mode）设计规范

> 状态：已落地（2026-08 三轮）。实现：`apps/general_erp/general_erp/public/css/erp_theme.bundle.css` 第 7 节。
> 切换入口：Desk 设置 → 主题（官方机制，在 `<html>` 上挂 `data-theme="dark"`）。

## 1. 设计原则

1. **不发明第二套设计**：夜间模式是同一套 token 的第二组取值，不新增组件样式；所有差异通过变量翻转；
2. **对齐官方 dark 标度**：frappe v16 官方 dark 已定义 `--surface-* / --ink-* / --outline-*` 新 token（顶栏、弹窗、部分卡片在用），本主题的中性色直接取官方值，避免「官方组件黑、我们的组件灰」的色差割裂；
3. **分层靠亮度阶**：页面底（最暗）→ 卡片（+1 阶）→ hover/浮层（+2 阶），每阶亮 6-10 个色阶，不用饱和度分层；
4. **主色提亮**：品牌蓝从 `#2563eb` 提亮到 `#3b82f6`，保证深底上 ≥ 4.5:1 对比；
5. **功能色浅底改半透明**：浅色模式的实色浅底（如 `#e8ffea`）在深色下改为同色 16% 透明度，避免「荧光贴片」；
6. **阴影加深、边框承重**：深色下投影对比度下降，分层主要靠 1px 边框（`--erp-border-1`）。

## 2. Token 映射表（light → dark）

| Token | Light | Dark | 对齐官方 |
|---|---|---|---|
| `--erp-bg-page` | `#f2f4f9` | `#0f0f0f` | `--surface-white` / `--surface-menu-bar` |
| `--erp-bg-card` | `#ffffff` | `#1c1c1c` | `--surface-cards` |
| `--erp-bg-hover` | `#f4f5f9` | `#2b2b2b` | `--surface-gray-2` |
| `--erp-bg-muted` | `#f7f8fb` | `#232323` | `--surface-gray-1` |
| `--erp-text-1` | `#1d2129` | `#f8f8f8` | `--ink-gray-9` |
| `--erp-text-2` | `#4e5969` | `#d4d4d4` | `--ink-gray-8` |
| `--erp-text-3` | `#86909c` | `#afafaf` | `--ink-gray-7` |
| `--erp-text-disabled` | `#c9cdd4` | `#717171` | `--ink-gray-3` |
| `--erp-border-1` | `#e6e8f0` | `#343434` | `--outline-gray-2` |
| `--erp-border-2` | `#c9cdd4` | `#424242` | `--outline-gray-3` |
| `--erp-border-light` | `#edeff4` | `#2b2b2b` | `--surface-gray-2` |
| `--erp-primary` | `#2563eb` | `#3b82f6` | （品牌保持，提亮） |
| `--erp-primary-light` | `#dbeafe` | `rgba(59,130,246,.22)` | — |
| `--erp-primary-lighter` | `#eff6ff` | `rgba(59,130,246,.12)` | — |
| `--erp-success(-text)` | `#00b42a` / `#009a29` | `#1ba964` / `#58c08e` | `--ink-green-2/3` |
| `--erp-warning(-text)` | `#ff9f0a` / `#cc7a00` | `#e37d00` / `#e79913` | `--ink-amber-2/3` |
| `--erp-error(-text)` | `#f53f3f` / `#cb2634` | `#e43838` / `#fc7474` | `--ink-red-3/4` |
| `--erp-info(-text)` | `#2563eb` / `#1d4ed8` | `#3294e3` / `#5aaef2` | `--ink-blue-2/3` |
| `--erp-*-light`（浅底） | 实色浅底 | 同色 16% 透明 | `--surface-*-1` 语义一致 |
| `--erp-shadow-1/2/3` | `rgba(29,33,41,.05/.07/.1)` | `rgba(0,0,0,.4/.5/.55)` | — |

## 3. 实现机制（为什么一处翻转即可全局生效）

1. 官方切换主题 = 在 `<html>` 上设 `data-theme="dark"`（属性选择器特异性 `0,1,0`，与 `:root` 相同）；
2. 本主题加载顺序**晚于**官方 desk bundle → 同特异性下本主题胜；
3. 第 2 节把所有 frappe 遗留变量（`--bg-color/--fg-color/--text-color/--border-color/--gray-*` 等）统一映射到 `var(--erp-*)`，CSS 变量**使用点求值** → 第 7 节在 `[data-theme="dark"]` 上重定义 `--erp-*`，整棵变量树自动翻转；
4. 官方 dark 块自己维护的新 token（`--surface-*/--ink-*/--outline-*`）与部分 legacy 映射（`--bg-blue/--alert-*` 等）保持官方值，不重复定义；
5. **坑**：一期曾把 legacy 变量硬编码成浅色实值（不经 `--erp-*`），导致 dark 下「半黑半白」——任何新增覆盖必须走 `var(--erp-*)`。
6. **坑**：CSS 注释内不能出现 `*/` 序列（如 `--surface-*/--ink-*` 连写）。bench build 的 minifier 按「第一个 `*/`」截断注释，残留文本会并入下一条规则的选择器，整条规则被浏览器丢弃（本次即 dark token 块整体失效）。

## 4. 组件级注意点

| 场景 | 规则 |
|---|---|
| 列表页 / 表单页白画布 | `var(--erp-bg-card)`，dark 下即 `#1c1c1c`，与工具栏连续 |
| 首页磁贴 / 文件夹芯片 | 磁贴 `var(--erp-bg-card)`；文件夹芯片固定 `#0289f7`（品牌色块，双主题一致） |
| 通知抽屉 / 顶栏通知弹层 | `var(--erp-bg-card)` + 细边框 + 深阴影（官方取 `--bg-color` 会拿到页面灰，已覆盖） |
| 输入控件 | 官方 dark 自行映射（`--control-bg` 等），不重复定义 |
| 图表 | 官方 dark 适配坐标轴/网格色；自绘 Tooltip 用 `var(--erp-bg-card)` |
| 打印格式 / 邮件模板 | **不参与**主题切换（固定浅色），不受本规范影响 |

## 5. 验收清单（切换主题后逐页过）

- [ ] 首页磁贴：深底磁贴 + 浅色文字，图标芯片不缺失
- [ ] 列表页：白(深)画布连续、表头/行分割线可见、hover 可辨
- [ ] 表单页：整页同底、右侧栏分割线、评论/活动区同底
- [ ] Workspace / 数据面板：深灰底 + 深卡片，KPI/图表文字可读
- [ ] 通知抽屉与顶栏通知弹层：深卡片底、边框/阴影分层
- [ ] 弹窗 / 下拉菜单 / Awesomebar：官方 dark，文字可读
- [ ] 徽标/状态 pill：半透明功能色底 + 对应深色文字
- [ ] 滚动条、selection、focus 环：`color-scheme: dark` 生效（官方 dark 块设置）
