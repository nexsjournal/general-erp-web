# 06 · 动效系统（Motion）

## 1. 原则

1. 动效传达**因果与层级**（谁引起谁、谁在上层），不做装饰性动画；
2. ERP 是高频工具：**能不动就不动**，动则短、快、稳；
3. 全程 60fps：只动画 `transform` / `opacity`（+ 少量 `box-shadow`），不触发布局属性（width/height/top/left）；
4. 尊重系统设置：`prefers-reduced-motion: reduce` 时全部降级为瞬时（duration 0）。

## 2. 时长阶梯

| Token | 值 | 场景 |
|---|---|---|
| `--erp-duration-fast` | 120ms | hover/active 变色、按下、badge |
| `--erp-duration-base` | 200ms | 弹层开合、抽屉、tab 指示条、下拉 |
| `--erp-duration-slow` | 320ms | 页面级转场、卡片展开 |
| 上限 | 500ms | 超过即过度，禁止 |

## 3. 缓动（Easing）

| Token | 值 | 用途 |
|---|---|---|
| `--erp-ease-out` | `cubic-bezier(0, 0, 0.2, 1)` | 元素**进入**（淡入、滑入、展开） |
| `--erp-ease-in` | `cubic-bezier(0.4, 0, 1, 1)` | 元素**退出**（淡出、收起） |
| `--erp-ease-in-out` | `cubic-bezier(0.4, 0, 0.2, 1)` | 位置移动（tab 条、抽屉滑入） |
| linear | — | 仅限进度条、loading 旋转 |

- 进出不对称：进入 ease-out，退出 ease-in（进入快收尾，退出加速离场）；
- ERP 场景禁用 bounce/overshoot（spring 回弹）。

## 4. 微交互（Micro-interactions）

| 对象 | 行为 | 参数 |
|---|---|---|
| 按钮按下 | `transform: scale(0.98)` + active 色 | 120ms |
| 卡片 hover | 边框 `--erp-border-2` + `--erp-shadow-2` + `translateY(-1px)`（仅可点击卡） | 150ms ease-out |
| 磁贴（首页） | hover 上浮 2px + shadow-2 | 150ms |
| 下拉/弹层进入 | opacity 0→1 + `translateY(-4px)→0`（下拉）/ `translateY(8px)→0`（底部抽屉式） | 200ms ease-out |
| 弹层退出 | 仅 opacity→0（scale 收缩禁用，避免内容跳位） | 120ms ease-in |
| 抽屉 | `translateX(100%)→0`，遮罩同步淡入 | 250ms ease-in-out |
| Toast 进入 | 顶部 `translateY(-16px)+opacity 0 → 0/1` | 200ms ease-out；退出反向 150ms |
| 骨架屏 | 微光带扫过（background-position） | 1.2s linear 循环 |
| 刷新图标 | 点击旋转 360° | 600ms linear，可连击 |
| 行内删除 | 行高收起（grid-template-rows 1fr→0fr 技巧） | 200ms ease-in |

## 5. 页面转场（Desk 内路由）

- 同页 Tab/列表切换：内容区 opacity 0→1（150ms），**不做整页滑动**（ERP 频繁切换，位移感会晕）；
- Workspace 进入模块：内容区 opacity + `translateY(4px)→0`（200ms ease-out）；
- 首次进入新模块：内容 200ms 淡入，KPI 数字可计数动画（见下）。

## 6. 数据动效

- **KPI 计数**：首次渲染从 0 计到目标值，400ms ease-out，tabular-nums 防抖动；刷新（新数据）时旧值 150ms 淡出、新值淡入，**不重放计数**；
- **图表**：
  - 首次绘制：300ms ease-out（线：从左到右描边生长；柱：从基线生长；环：从 12 点方向展开）；
  - 数据更新：200ms 数值/路径 morph（直接插值，不做旋转重绘）；
  - 图例 hover 高亮对应系列，其余系列降至 40% 透明（150ms）；
- **列表行**：分页/筛选后 200ms 整体淡入（不做逐行 stagger，ERP 行数多会拖沓）；仅「新增 1 行」场景新行 150ms 淡入高亮 1s（`--erp-primary-lighter` 底渐隐）。

## 7. 禁止清单

- 禁止：视差滚动、自动轮播、无限循环的非 loading 动画、文字逐字浮现、3D 翻转；
- 禁止对大表格（>50 行）整体做入场动画；
- 动效参数修改必须同步本文档 token，代码中不出现魔法数值。
