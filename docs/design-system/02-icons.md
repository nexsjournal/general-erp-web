# 02 · 图标系统（Icons）

## 1. 来源与风格

- **基座图标**：frappe 内置 `es-line-*`（outline 线性风格，feather 系），SVG sprite 引入（`<use href="#es-line-xxx">`）。
- **自定义图标**：必须与基座同风格——线性、圆角端点、统一描边；放入 `apps/general_erp/general_erp/icons/`，sprite 合并后以 `erp-` 前缀命名。
- **禁用**：emoji 作功能图标、实心/线性混排同一层级、第三方彩色图标（品牌 logo 类除外）。

## 2. 规格

| 项 | 规范 |
|---|---|
| 设计网格 | 24×24px，内边安全区 2px（实际绘图区 20×20） |
| 描边 | 1.5px（16px 渲染时）/ 2px（24px 渲染时），`stroke-linecap/linejoin: round` |
| 颜色 | 一律 `currentColor`，由所在控件的文本色控制，不写死 |
| 渲染档位 | 16px 行内（表头/字段/按钮内）；20px 导航项；24px 空状态/磁贴内 |
| 文件 | SVG 单色、无 fill（除品牌磁贴反白场景）、压缩去 meta |

## 3. 尺寸与场景

| 场景 | 尺寸 | 示例 |
|---|---|---|
| 按钮内（icon+文字） | 16px，与文字间距 6px | 新增、导出 |
| 表格列头排序/操作 | 14-16px | 排序、行操作 |
| 顶栏（搜索/通知/设置） | 18-20px | ⌘K 搜索、铃铛 |
| 空状态插画位 | 40-48px（线性大图） | 列表无数据 |
| Workspace 磁贴 | 磁贴 56×56px 圆角 12px 实心底 + 白色 24px 图标 | 首页 12 宫格 |

## 4. Workspace 磁贴（首页图标格）

- 磁贴：56×56px，`border-radius: 12px`；
- 底色：模块主色（用 1.4 图表色序按模块固定映射，全站稳定不变）或品牌蓝；当前选中模块用 `--erp-primary`；
- 图标：白色 24px 线性；
- 磁贴下标签：13px `--erp-text-2`，单行，超出省略号；
- hover：磁贴上移 2px + `--erp-shadow-2`，150ms（见 06-motion）。

## 5. 命名

- 基座沿用 `es-line-{name}`；
- 自定义：`erp-{对象}-{形态}`，如 `erp-invoice-outbox`；
- 状态图标（成功/警告/错误/信息）只用功能色 + 固定 4 枚：`check-circle` / `alert-triangle` / `alert-circle` / `info`。
