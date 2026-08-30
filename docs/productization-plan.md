# 产品化（去开源化）设计方案

> 目标：把基于 Frappe/ERPNext 二开的系统做成可售卖的独立产品。
> 结论先行：**"删掉界面上的开源信息"只能做到 UI 层 80%，剩下 20% 是法律与架构问题，必须用户拍板，不能靠"删字"解决。**

## 一、开源痕迹三层模型（侦察实测结果）

### L1 UI 可见层（用户/客户肉眼可见）——大部分已清理
| 痕迹 | 位置 | 状态 |
|---|---|---|
| 登录页脚"由 ERPNext 驱动" | login.html footer | ✅ 已用 app 级模板覆盖抹除（templates/includes/footer/footer_powered.html） |
| 侧边栏 21 个英文开源工作台（Build/Selling/Stock…） | Workspace | ✅ 已隐藏 18 个 + "ERPNext Settings"改名"系统设置"，普通用户只剩：报表中心/ERP工作台/系统设置 |
| 浏览器标签标题 | site_config | ✅ site_name 已设（页面 <title> 仍显示 Login，需 brand logo 阶段统一） |
| 登录页 Logo | erpnext-favicon.svg / logo | ⏳ 待产品 Logo 素材（T2） |
| 浏览器 Favicon | erpnext-favicon.svg | ⏳ 同上 |

### L2 技术元数据层（开发者/抓包可见，终端客户基本不可见）
- 前端 JS 资源路径 "/assets/erpnext/..."（抓包可见）
- 所有 API 路径 "/api/method/frappe.*"、Cookie 名、User-Agent 特征
- HTTP 响应头、错误堆栈里的 frappe/erpnext 模块路径
- DocType/Role 元数据（"Desk User"等角色名）
- **评估**：卖给客户日常使用完全无感知；只有懂技术的人审查服务器或抓包才能发现。商业上通常可接受，改不干净（改=重写 frappe 框架，不现实）。

### L3 法律层（最关键，删任何代码都改变不了）
frappe 与 erpnext 均为 **AGPL-3.0** 协议。AGPL 的核心约束：
1. 你修改/衍生它们的代码对外提供服务（SaaS）时，**必须向使用者公开你的完整源代码**（含 general_erp 与所有补丁）；
2. 不能以"闭源商业软件"名义销售 AGPL 衍生品的**源码交付义务**；
3. 界面删 logo/署名 **不等于** 豁免 AGPL 义务，反而可能被认定为"故意移除声明"（AGPL §5 要求保留原作者版权声明）。

**三条合规路径（需用户拍板，选哪条决定后面所有动作）：**

| 方案 | 做法 | 成本 | 风险 |
|---|---|---|---|
| A. AGPL 合规商用（推荐起步） | 保留基座，产品按 AGPL 规则交付：向客户披露基座为 AGPL 开源 + 提供你的 general_erp 源码（基座本就可从 GitHub 公开获取，披露无商业秘密损失）。合同写明"软件基于开源框架开发"。 | 低（几乎零开发） | 无法律风险；客户若在意"源码可见"需在商务上管理预期 |
| B. 商业双授权 | 与 Frappe Technologies 谈 ERPNext 商业授权（其官方有 ERPNext Commercial License 渠道），获得闭源分发权 | 高（商务谈判+费用） | 谈判周期不可控 |
| C. 自建替换基座 | 抛弃 frappe/erpnext，仅保留 general_erp 业务逻辑，重写框架层 | 极高（等于重写一个 ERP 平台，月级→年级） | 不现实，仅长期路线 |

> 我的建议：**售前阶段走 A**。理由：你的核心资产（外贸业务流、报表、审批流、邮件体系）全在 general_erp 里，基座代码公开不构成竞争威胁；界面已做到客户无感知开源痕迹。B 作为有付费大客户时的升级选项。

## 二、产品命名与品牌落地（依赖 T2 素材）
1. 产品名（例："外贸云 ERP"，待定）：
   - hooks.py app_title、site_config site_name、登录页 logo/副标题、favicon
   - 邮件发件署名、报表导出文件名前缀
2. 需要用户提供的素材：产品名、Logo（svg/png）、favicon、品牌色
3. 落地后回归：登录页截图走查 + 18 报表 + 6 角色菜单

## 三、部署形态（卖给客户怎么交付）
| 形态 | 说明 | 建议 |
|---|---|---|
| 私有化部署（推荐起步） | 每个客户一套 bench+MariaDB+Redis，交付部署手册+备份脚本 | 与现有 start_dev.sh 体系复用，加 scripts/deploy.sh |
| SaaS 多站点 | 一台服务器跑多 site（frappe 原生支持，每客户一个 site） | 中期方向，省运维 |
- 部署红线（按全局规则）：HTTPS、/health 健康检查、发版前 DB 备份、回滚方案、冒烟脚本 scripts/smoke.sh

## 四、已执行 & 未执行边界
**已执行（本会话，UI 安全层）**：
- 页脚开源署名抹除（app 级模板覆盖，不动 frappe 源码，符合项目"只写 general_erp"约定）
- 18 个英文开源工作台隐藏 + 系统设置改名（站点级数据，非代码）
- 站点标题设置
**未执行（等拍板）**：L3 法律方案、产品名/Logo、部署脚本、生产任务单定制（T1）

## 五、待用户拍板
1. 法律路径 A/B/C 选哪个？（推荐 A，零成本起步）
2. 产品名 + 提供 Logo/favicon 素材
3. 交付形态：先私有化还是直接多站点 SaaS？

