# 开源 ERP 系统选型调研报告

> 调研目标：寻找**评价高、适配性强、性价比高、完全开源可改造**的完整 ERP 系统，作为自研 ERP 的底座。
> 数据来源：GitHub API / Gitee / SourceForge / 各项目官网（数据抓取时间：2026-08-26）。
> Star 数等指标均为抓取当日 GitHub 实时数据。

---

## 一、结论速览（TL;DR）

| 排名 | 项目 | 一句话结论 |
|---|---|---|
| ⭐ 首选 | **ERPNext** | 100% 开源（GPL-3.0，无企业版阉割）、功能最完整的免费 ERP，Frappe 框架二开门槛低，最适合"基于它改造"的诉求 |
| 强力候选 | **Odoo Community** | 生态/口碑/社区规模最大，但**财务本地化、Studio 等关键能力在闭源企业版**，与"完全开源"诉求有冲突，需接受边界 |
| 备选（Java 团队/国产化优先） | **jshERP（管伊佳ERP）** | 国产 Apache-2.0，SpringBoot + Vue，进销存+财务+生产开箱即用，中文体验最好；单人维护、功能深度有限 |
| 备选（PHP 技术栈） | **Dolibarr** | 老牌 GPL 纯开源、模块化、部署轻；偏欧洲中小企业场景，制造业能力弱 |
| 观察项 | **AureusERP** | MIT 协议、Laravel + Filament 现代栈、2025 年项目增长极快（11.8k stars），但太年轻，长期风险未验证 |

**推荐路径**：先花 1~2 天分别本地部署 **ERPNext v16** 与 **Odoo 19 Community** 跑通核心业务流（采购→销售→库存→财务），再结合团队技术栈（Python vs Java）做最终决策。若团队是 Java 技术栈且业务以进销存+财务为主，直接选 **jshERP** 二开成本最低。

---

## 二、候选项目总表

| 项目 | GitHub Stars | 协议 | 技术栈 | 首次发布 | 最新版本 | 最近提交 | 完整度 | 完全开源 |
|---|---|---|---|---|---|---|---|---|
| [ERPNext](https://github.com/frappe/erpnext) | 38.5k | **GPL-3.0** | Python / Frappe / MariaDB | 2011 | v16.33.0（2026-08） | 2026-08-26 | ★★★★★ | ✅ 是 |
| [Odoo](https://github.com/odoo/odoo) | 53.9k | LGPL-3.0（社区版）；企业版 OPL-1 私有 | Python / PostgreSQL | 2005（2014 上 GitHub） | 19.0 | 2026-08-26 | ★★★★★ | ⚠️ 部分（关键模块在企业版） |
| [Dolibarr](https://github.com/Dolibarr/dolibarr) | 7.5k | GPL-3.0 | PHP / MySQL | 2011 | 24.0.0（2026-08） | 2026-08-26 | ★★★★ | ✅ 是 |
| [AureusERP](https://github.com/aureuserp/aureuserp) | 11.8k | MIT | PHP Laravel 13 / Filament 5 / MySQL | 2025-01 | v1.5.0（2026-08） | 2026-08-24 | ★★★★ | ✅ 是 |
| [jshERP 管伊佳ERP](https://github.com/jishenghua/jshERP) | 4.5k | Apache-2.0 | Java SpringBoot / Vue2 / MySQL | 2016 | v3.5（2024-11） | 2026-08-19 | ★★★☆ | ✅ 是 |
| [InvenTree](https://github.com/inventree/InvenTree) | 7.4k | MIT | Python Django / React | 2017 | 1.5.2（2026-08） | 2026-08-25 | ★★★（库存/生产向） | ✅ 是 |
| [IDURAR ERP CRM](https://github.com/idurar/idurar-erp-crm) | 8.7k | AGPL-3.0 | MERN / React | 2020 | — | 2026-08-14 | ★★☆ | ✅ 是 |
| [Gauzy](https://github.com/ever-co/ever-gauzy) | 4.3k | AGPL-3.0 | NestJS / React | 2019 | v111（2026-08） | 2026-08-26 | ★★★（业务管理向） | ✅ 是 |
| [Metasfresh](https://github.com/metasfresh/metasfresh) | 2.4k | GPL-3.0（CompiERP 系） | Java / PostgreSQL | 2015 | 5.175（2023-06） | 2026-08-25 | ★★★★（食品/物流向） | ✅ 是 |
| [Akaunting](https://github.com/akaunting/akaunting) | 10.1k | 核心免费 + 商业模块 | PHP Laravel / MySQL | 2017 | — | 2026-08-25 | ★★（仅财务） | ⚠️ 部分 |
| [Metabase 系低代码：NocoBase](https://github.com/nocobase/nocobase) | 23.9k | 核心 Apache-2.0 + 企业插件收费 | TypeScript / Node / PostgreSQL | 2020 | — | 2026-08-26 | 平台（非成品 ERP） | ⚠️ 部分 |
| [yudao / ruoyi-vue-pro](https://github.com/YunaiV/ruoyi-vue-pro) | 39.0k | MIT | Java SpringBoot / Vue3 | 2020 | — | 2026-08-14 | 后台框架 + ERP 模块 | ✅ 是（ERP 模块较浅） |
| [Apache OFBiz](https://ofbiz.apache.org) | 807（镜像仓） | Apache-2.0 | Java / PostgreSQL | 2001 | — | 主干持续维护，GitHub 镜像停滞 | ★★★★ | ✅ 是 |
| [iDempiere](https://github.com/idempiere/idempiere) | 655 | BSD 风格自定义 | Java / MySQL | 2003 | — | 2026-08-25 | ★★★ | ✅ 是 |
| [Openbravo](https://www.openbravo.com) | GitHub 空壳仓（主仓在 SourceForge/私有） | GPL-3.0 | Java / PostgreSQL | 2006 | — | — | ★★★★（开源版能力有限） | ⚠️ 商业化导向 |
| [Steedos](https://github.com/steedos/steedos-platform) | 1.6k | AGPL-3.0 | TypeScript | 2019 | — | 2026-08-25 | 平台（低代码） | ⚠️ 有商业版 |
| [Carbon](https://github.com/crbnos/carbon) | 2.4k | 自定义（含 `packages/ee` 商业授权） | TypeScript / Next.js | 2024-06 | — | 2026-08-26 | ★★★★（制造 ERP/MES） | ❌ 否（有 EE 目录） |
| [WebVella ERP](https://github.com/WebVella/WebVella-ERP) | 1.5k | Apache-2.0 | C# ASP.NET Core 9 / PostgreSQL | 2015 | — | 2026-08-04 | ★★★ | ✅ 是 |
| [open-mercato](https://github.com/open-mercato/open-mercato) | 1.7k | MIT | TypeScript / Next.js | 2025-09 | v0.6.7（2026-08） | 2026-08-26 | ★★★（CRM/ERP 框架） | ✅ 是 |
| [FJ-OMS/oms-erp](https://github.com/FJ-OMS/oms-erp) | 1.9k | Apache-2.0 | Java | 2022 | — | 2025-12-24 | ★★★（OMS/WMS/财务中台，国产） | ✅ 是 |

> 说明：
> - "完整度"指覆盖 采购/销售/库存/财务/生产/HR/项目 等 ERP 核心域的广度与深度。
> - "完全开源"指：核心功能不藏闭源模块、协议允许自由商用与二次开发。
> - 平台覆盖：以上项目主仓均在 GitHub；Dolibarr / OFBiz / iDempiere / Openbravo 同时托管于 SourceForge；jshERP 在 Gitee 有镜像；NocoBase / Steedos 有国内部署方案。

---

## 三、重点项目深度分析

### 3.1 ERPNext ⭐（首选）

- **仓库**：`frappe/erpnext`，38.5k stars / 12.6k forks，2011 年启动，Frappe Technologies（有商业融资支持的公司）主导。
- **许可**：GPL-3.0，**无企业版分支**——所有功能（财务、制造、HR、项目）全部开源，这是它与 Odoo 最大的区别，也最贴合"完全开源可改造"的要求。
- **功能覆盖**：会计（多公司/多币种/总账/损益）、采购、销售、库存、**制造（BOM/工作中心/车间作业/外包）**、HR 与薪资、项目、资产、质量、CRM、教育/农业/非营利等行业模块，电商与多语言内置。
- **二开适配性（关键）**：
  - 基于 **Frappe Framework**：新业务实体 = 声明式 DocType（YAML/JSON 定义 + 少量 Python 钩子），改字段、加单据、定制逻辑基本不碰框架核心；
  - 自带工作流、权限、打印格式、REST API、Websocket 实时能力；
  - 前后端一体（Frappe 自带 UI），也支持独立前端通过 API 对接；
  - 有官方 Docker 镜像（`frappe/erpnext`），部署成本低。
- **社区与版本节奏**：v15/v16 双维护线（v16.33.0，2026-08 仍在更新），issue 响应活跃，官方文档齐全，有 Frappe School 免费课程。
- **风险/短板**：
  - **中文本地化**：UI 有社区翻译但完整度一般；中国特有的税票、金税、社保、银行对接需自己开发（这正是你的自研空间）；
  - 技术栈是 Python/MariaDB，Java 团队接手需要学习曲线；
  - 深度定制后升级主线版本的成本需要预留（社区常见操作：基于 fork 维护私有分支）。

### 3.2 Odoo（强力候选，但有"开源边界"问题）

- **仓库**：`odoo/odoo`，53.9k stars，全球最大开源 ERP 生态，60+ 应用（CRM、库存、制造、POS、电商、HR…）。
- **许可与边界（务必注意）**：
  - 社区版 = **LGPL-3.0**，可自由改造商用；
  - 但 **完整会计与各国税务本地化（含中国）、Studio 低代码设计器、高级报表/BI、部分电商与行业模块在企业版（OPL-1 私有协议，闭源）**。
  - 结论：如果你需要"完整财务"且坚持全链路开源，Odoo 社区版财务能力不够用；若接受"社区版底座 + 自建财务模块 + 不依赖 Studio"，Odoo 仍是生态最好的选择。
- **二开适配性**：Odoo ORM + 模块继承机制成熟，开发者文档完善，第三方模块市场（Odoo Apps / OCA 社区仓库，数千模块）；Python/PostgreSQL。
- **版本节奏**：每年一个大版本（当前 19.0，2025-10 发布），LTS 由社区/企业版支持。
- **适合**：团队能接受社区/企业版边界、或业务侧重 CRM+供应链而非深财务的场景。

### 3.3 jshERP 管伊佳ERP（国产 Java 路线首选）

- **仓库**：`jishenghua/jshERP`（原华夏ERP），4.5k stars / 1.5k forks，**Apache-2.0，明确可商用**。
- **定位**：国产开源 ERP 中人气最高，专注 **进销存 + 财务 + 生产**，零售/采购/销售/仓库/财务/报表模块开箱即用，73 种界面语言。
- **技术栈**：SpringBoot 2.0 + MyBatis + Vue2 + Ant Design + MySQL + Redis，基于 Jeecg-Boot；JDK8，国内团队上手零成本。
- **优点**：中文文档/视频教程/部署包齐全，SaaS 多租户架构（自带租户体系），二次开发对 Java 团队最友好。
- **风险/短板**：
  - **单人维护**（作者 jishenghua），社区贡献弱于国际项目；
  - 最近正式 release 是 v3.5（2024-11），主干仍在提交但发版节奏慢；
  - 功能深度有限：制造较浅、无完整 HR/项目模块、无 MES；
  - 框架偏旧（SpringBoot 2 / Vue2），长期二开需考虑升级成本。
- **适合**：业务 = 进销存 + 财务 + 简单生产，团队是 Java，追求"中文开箱 + 低二开成本"。

### 3.4 Dolibarr（欧洲老牌，纯开源稳健）

- **仓库**：`Dolibarr/dolibarr`，7.5k stars，**GPL-3.0 纯开源无企业版**，2011 年至今，v24（2026-08 发布），Core Infrastructure 最佳实践徽章。
- **架构**：模块化（400+ `mod_*` 模块），PHP/MySQL，单机 Docker 即部署，维护成本极低。
- **功能**：联系人、报价、订单、发票、库存、采购、制造（简单）、HR、ECM；偏中小企业日常经营，制造业深度不足。
- **社区**：欧洲（尤其法/德/西）用户基础大，论坛与商业伙伴支持网络成熟；中文文档少。
- **适合**：PHP 团队、业务以贸易/服务为主、追求极简运维。

### 3.5 AureusERP（高增长观察项）

- **仓库**：`aureuserp/aureuserp`，**MIT**（候选中协议最宽松），11.8k stars。
- **技术栈**：Laravel 13 + FilamentPHP 5 + PHP 8.3+，现代化 PHP 栈，UI 观感好。
- **功能**：CRM、库存、会计、生产、HR、文档，带 **插件系统**（插件可独立安装/更新），二开走 Laravel 生态。
- **风险**：仓库 2025-01 创建，**不到 2 年冲到 11.8k stars**（增长曲线偏营销驱动），长期维护记录不足，财务模块深度未经大规模验证。
- **适合**：PHP/Laravel 团队、业务复杂度中等、可接受早期项目风险。

### 3.6 其他值得关注的方向（非"完整 ERP"，按场景补充）

| 项目 | 定位 | 何时考虑 |
|---|---|---|
| **InvenTree**（MIT, 7.4k） | 库存/BOM/采购/生产工作流，制造行业口碑极好 | 业务重心在**制造与库存**，财务用其他系统补齐 |
| **NocoBase**（23.9k） | 无代码/低代码业务系统平台（核心 Apache-2.0，部分插件收费） | 想"自己搭"而不是"改成品"，快速拼出 ERP 形态 |
| **ruoyi-vue-pro / yudao**（MIT, 39k/19k） | Java 后台框架，内置较浅的 ERP/CRM/MES 模块 | Java 团队自建为主、ERP 模块只做起点 |
| **Gauzy**（AGPL, 4.3k） | 业务管理平台：HRM/PM/CRM/工时/时间追踪 | 团队管理类业务为主，非传统 ERP |
| **Metasfresh / OFBiz / iDempiere / Openbravo** | CompiERP 系的 Java 老项目，或 OFBiz 这类重量级方案 | 特定行业（食品/物流）或有 Java 遗留能力要求时再评估 |
| **Carbon**（2.4k） | 制造 ERP/MES，Next.js 栈，社区活跃 | 注意其 `packages/ee` 为商业授权，**不完全开源**，仅观察 |
| **open-mercato**（MIT, 1.7k） | "AI 工程基座 + CRM/ERP 模块"，2025-09 创建 | 尝鲜：Next.js + AI 辅助开发的新一代形态，尚不成熟 |
| **FJ-OMS/oms-erp**（Apache-2.0, 1.9k） | 国产全渠道 OMS/WMS/财务中台 | 电商多渠道路由、仓储场景 |

---

## 四、关键维度横向对比（前五名）

| 维度 | ERPNext | Odoo CE | jshERP | Dolibarr | AureusERP |
|---|---|---|---|---|---|
| 完全开源 | ✅ 无企业版 | ⚠️ 财务/Studio 在企业版 | ✅ | ✅ | ✅ |
| 商用许可风险 | GPL-3.0（注意传染性，SaaS 需评估 AGPL 式义务；GPL 对内部部署/私有部署影响小） | LGPL-3.0 | Apache-2.0（最宽松） | GPL-3.0 | MIT（最宽松） |
| 财务完整度 | ✅ 完整 | ❌ 社区版仅基础记账 | ✅ 完整（中国习惯） | ✅ 基础完整 | ✅ 中等 |
| 制造/生产 | ✅ 强 | ✅ 强（社区版基础+企业版增强） | ⚠️ 简单生产 | ⚠️ 简单 | ⚠️ 中等 |
| HR/薪资/项目 | ✅ | ✅（部分企业版） | ❌ 弱 | ⚠️ 基础 | ✅ 中等 |
| 多公司/多币种/多租户 | ✅ / ✅ / ✅ | ✅ / ✅ / ✅ | 多租户 ✅ | ✅ / ⚠️ | ⚠️ |
| 二开体验 | Frappe DocType，快，Python | Odoo ORM，成熟，Python | Java+Vue，模板化生成 | PHP 模块，简单直接 | Laravel+Filament，现代化 |
| 中文生态 | 社区翻译，本地化需自建 | 社区 l10n + 第三方模块 | ✅ 原生中文 | 弱 | 弱 |
| 团队栈匹配 | Python | Python | **Java** | PHP | PHP |
| 维护主体 | 公司（Frappe）+ 社区 | 公司（Odoo SA）+ 社区 | **个人** | 社区 + 商业伙伴 | 公司（早期） |
| 版本活跃 | 2026-08 在更 | 2026-08 在更 | 主干在更，发版慢 | 2026-08 在更 | 2026-08 在更 |

---

## 五、性价比分析

所有候选 License 费用均为 0，"性价比"主要体现在：

1. **二次开发成本**（占大头）
   - 团队是 Java → `jshERP`（栈一致、中文文档）或 yudao 自建；
   - 团队是 Python/愿意学 → `ERPNext`（框架化程度最高，改单据最快）或 Odoo；
   - 团队是 PHP → `AureusERP` / `Dolibarr`。
2. **被"企业版"绑架的风险**（隐性成本）
   - Odoo 社区版做完整财务需自建或转向企业版（按用户订阅收费），长期可能侵蚀"免费"优势；
   - NocoBase / Steedos / Carbon 均有商业插件/EE 目录，属"开源底座 + 商业增值"模式，与"完全开源"诉求需权衡。
3. **运维成本**：ERPNext / Odoo / Dolibarr / jshERP 均有 Docker 一键部署，单机 2C4G 可跑中型业务，成本相当。
4. **升级成本**：大版本节奏快的项目（Odoo 年更、ERPNext 年更）要求跟进升级能力；jshERP / Dolibarr 升级压力小。

---

## 六、建议与下一步

1. **POC 验证（1~2 天）**：
   - 部署 ERPNext v16 Docker（`frappe/erpnext`），走通：建商品 → 采购入库 → 销售出库 → 应收/应付 → 总账报表；
   - 部署 Odoo 19 Community 同样流程，对比财务断点；
   - 若团队 Java，同时跑 jshERP 的部署包。
2. **决策清单**（POC 后确认）：
   - 业务是否需要完整制造（BOM/车间）？→ 是：ERPNext / Odoo；否：jshERP / Dolibarr 够用；
   - 是否强依赖中国税务/金税/发票？→ 需评估各家 l10n_cn 现状（大概率都要自建，ERPNext/Odoo 框架内自建更规范）；
   - 团队技术栈与长期维护能力（Python 团队 vs Java 团队）；
   - 是否接受 GPL 协议对交付方式的影响（内部使用/私有部署基本无碍；若做成对外 SaaS 销售需法务评估）。
3. **长期策略建议**：无论选谁，都把"私有 fork + 按大版本跟进上游 + 定制层收敛到自定义模块/DocType"作为工程纪律，避免深度侵入核心导致无法升级。

---

## 附：数据快照（2026-08-26 抓取）

| 项目 | Stars | Forks | 协议 | 最新版本（日期） | 最近 push |
|---|---|---|---|---|---|
| frappe/erpnext | 38508 | 12598 | GPL-3.0 | v16.33.0（2026-08-25） | 2026-08-26 |
| odoo/odoo | 53947 | 33519 | LGPL-3.0（社区） | 19.0（分支 19.0） | 2026-08-26 |
| Dolibarr/dolibarr | 7535 | 3478 | GPL-3.0 | 24.0.0（2026-08-20） | 2026-08-26 |
| aureuserp/aureuserp | 11782 | 545 | MIT | v1.5.0（2026-08-04） | 2026-08-24 |
| jishenghua/jshERP | 4534 | 1503 | Apache-2.0 | v3.5（2024-11-11） | 2026-08-19 |
| inventree/InvenTree | 7447 | 1526 | MIT | 1.5.2（2026-08-25） | 2026-08-25 |
| idurar/idurar-erp-crm | 8720 | 3126 | AGPL-3.0 | — | 2026-08-14 |
| ever-co/ever-gauzy | 4348 | 871 | AGPL-3.0 | v111.39.1（2026-08-26） | 2026-08-26 |
| metasfresh/metasfresh | 2407 | 811 | 自定义（GPL 系） | 5.175（2023-06-27） | 2026-08-25 |
| nocobase/nocobase | 23850 | 2837 | 自定义（核心 Apache-2.0） | — | 2026-08-26 |
| YunaiV/ruoyi-vue-pro | 38970 | — | MIT | — | 2026-08-14 |
| YunaiV/yudao-cloud | 19442 | — | MIT | — | 2026-08-14 |
| akaunting/akaunting | 10091 | — | 自定义 | — | 2026-08-25 |
| WebVella/WebVella-ERP | 1482 | 538 | Apache-2.0 | — | 2026-08-04 |
| crbnos/carbon | 2379 | 340 | 自定义（含商业 EE） | — | 2026-08-26 |
| open-mercato/open-mercato | 1681 | 374 | MIT | v0.6.7（2026-08-05） | 2026-08-26 |
| FJ-OMS/oms-erp | 1918 | 357 | Apache-2.0 | — | 2025-12-24 |
| idempiere/idempiere | 655 | — | 自定义（BSD 风格） | — | 2026-08-25 |
| steedos/steedos-platform | 1574 | 413 | AGPL-3.0 | — | 2026-08-25 |
| apache/ofbiz（GitHub 镜像） | 807 | 552 | Apache-2.0 | — | 镜像停滞（主干在 Apache 仓库） |
