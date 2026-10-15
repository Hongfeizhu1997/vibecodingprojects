# SSG Sales AI 顶层设计

> 版本：v6（在 v5 基础上，将 EKP 知识底座能力融入架构，深化第 3~7 章）
> 状态：概念与方向草案，待 review
> 调研支撑：`references/industry-best-practices.md` + Obsidian `business/ekp-platform.md`
> v5 存档：`top-level-design.v5.md`

---

## 0. 文档定位

本文档在 SSG Sales AI Blueprint v4 之上做三件事：

1. **补上缺失的"交付层"**——把 blueprint 的"6 域 Agent + 编排层"升级为"角色化 Workspace（交付层）+ 域 Agent（引擎层）"的完整架构。
2. **用 industry best practice 细化 8 个补强方向**——共享上下文、协作协议、评估门禁、覆盖度度量等，让顶层设计从"概念"走到"可落地的方向与设计"。
3. **（v6 新增）把 EKP 落成架构的知识底座**——不再把 EKP 当成一个外挂的"RAG 知识库"，而是明确它在交付层、引擎层、共享上下文、质量门禁四个层面的具体作用，让"6 个域 Agent"从孤岛变成"有统一知识底座的整体"。
4. **（v6 新增）画清 Reuse vs Build 决策**——从高到低识别整个方案长什么样，显式标注每一层哪些复用企业已有能力（EKP / Skill Hub / 业务系统 / MCP-A2A 协议）、哪些必须自建。自建项不是缺陷，是方案的正当组成部分，纳入计划范围（详见 4.3 Build 清单）。

> v6 相对 v5 的核心变化：第 3~7 章每章新增 EKP 融入小节（3.5 / 4.2 / 5.4 / 6.3 / 7.5），并补全各章被 EKP 支撑起来的细节；新增 4.3「Build vs Reuse 决策地图」。

---

## 1. 定位与愿景

- **SSG Northstar**：Build and operate AI for the Modern Enterprise（为现代企业构建并运营 AI）。
- **本蓝图交付**：Inside Sales Transformation 的 AI 承诺（$1.8M 已批资金、30%→50% 流程自动化、SSIR 生产力 +15%、GPS MT $2.63B +17%）。
- **核心判断**（industry 共识，非口号）：AI in sales 已经不是一个"工具问题"，而是一个"基础设施问题"。Gartner 的失败模式警告——2028 年 Agent 数量是销售的 10 倍，却不到 40% 的人认可其生产力提升——本质是"没有共享上下文层 + 没有明确 owner"。

**因此，本蓝图的目标不是"多做几个 Agent"，而是"把 SSG 销售变成一个 AI-native 的整体"。**

这个"整体"的实现，除了共享上下文层之外，还需要一个**统一的知识底座**——这正是 EKP 在架构里的角色：6 个域 Agent 各干各的活，但都从同一个知识底座取数、同一个质量闭环进化。

---

## 2. 组织架构与 Workspace 对象（关键定位）

### 2.1 两层组织

| 层 | 组织 | 定位 | 与本蓝图关系 |
|---|---|---|---|
| 前台 | **ISO**（Inside Sales Organization） | 联想核心销售，卖硬件 + 服务 | **外部 interface 对象**，非 workspace 用户 |
| 后台 | **SSG**（Solutions & Services Group） | 服务产品 BG / owner，用专业能力支持 ISO | **workspace 的直接服务对象** |

SSG 作为服务产品的 owner，有对应的 **Sales team、Pricing team** 去支持 ISO 的 Sales team、Pricing team。

### 2.2 顶层设计的核心逻辑

```
SSG 内部先 AI 化（AI-native organization）
        ↓
SSG 作为一个整体对外 interface
        ↓
通过 ISO Entry Layer 支持 ISO 前台（seller / sales support / pricing）
```

这呼应 blueprint Slide 7（"Deploy EKM within SSG for ADW"）与 Slide 14（ISO Entry Layer 是 external）。**Workspace 是给 SSG 业务人员用的**，不是给 ISO 前台用的。

> v6 补充：Slide 7 的 "Deploy EKM within SSG" 落地时，不是新建一套知识管理，而是**复用已有的 EKP 平台**——EKM 是"要做知识管理"这个方向，EKP 是"用什么承载"这个产品。下文所有"知识底座"均指 EKP。

### 2.3 Persona（SSG 业务人员，workspace 用户）

| Persona | 使用的域能力 | 对外支持对象 |
|---|---|---|
| **SSG Sales team** | Customer Engagement + Config & Quote | 支持 ISO Sales |
| **SSG Pricing team** | Pricing | 支持 ISO Pricing |
| **Service Product Enablement team** | Service Product | 服务产品知识赋能 |
| **Service Sales Ops team** | Sales Ops（APoS） | 服务相关 operation |
| **Leasing / DWS team** | Leasing | 租赁（DWS） |

**未来扩展**：ISO Sales Ops team（整个 sales 过程 operation owner，ISO Sales Support 隶属其下）——预留扩展位，不进入当前 scope。

---

## 3. Workspace 交付层（本次核心新增）

### 3.1 定位：交付层 vs 引擎层

这是本次顶层设计最重要的补强。industry best practice（Salesforce Agentforce、Microsoft Copilot Studio、内部 SupplyX）共同指向：**Agent 的价值在"如何被组织成业务人员可持续消费的工作台"，不在 Agent 本身**。

```
┌─────────────────────────────────────────────┐
│  交付层  SSG Sales Workspace（按 persona 组织） │
│          · 6 个角色工作台视图                  │
│          · 覆盖度度量（L0–L4）                 │
│          · efficiency / data / insight 三类   │
└──────────────────┬──────────────────────────┘
                   │ 调用
┌──────────────────▼──────────────────────────┐
│  引擎层  6 个域 Agent（能力）                  │
│          · Service Product / Customer        │
│            Engagement / Config & Quote /     │
│            Pricing / Sales Ops / Leasing     │
│          · workflow 与 agent 区分             │
│          · 能力封装（Skill Hub）              │
└─────────────────────────────────────────────┘
```

**关键原则**：交付层调用引擎层，二者分层不重叠。blueprint 里已有的 "SSG Sales Workspace" 从编排层升级为真正的交付面。

### 3.2 Persona 划分（角色化，而非功能模块化）

按 SSG 业务团队组织工作台，而非按功能模块。每个 persona 一个专属视图，不是通用聊天窗（iChain Persona Workspace 的 "Persona-based" 原则）。

### 3.3 工作覆盖度度量（把"覆盖"变成可管理对象）

为每个 persona 列工作清单，标注覆盖度分级：

| 覆盖级别 | 含义 | 示例 |
|---|---|---|
| L0 | AI 未覆盖 | 纯人工 |
| L1 | AI 辅助（人工主导） | AI 查知识、人做决策 |
| L2 | AI 建议（人工决策） | AI 出报价/定价建议，人审批 |
| L3 | AI 主导（人工例外） | AI 自动报价，异常才人工 |
| L4 | AI 自主 | 自主定价、自主审批标准单 |

覆盖度既是设计目标，也是给管理层看的价值证明（比"准确率"好懂）。

### 3.4 三类 Benefit 落到 persona（效率 / data / insight 闭环）

- **Data（看）**：统一数据模型上的自助查询、可视化
- **Insight（判断）**：主动推送——客户倾向、价格机会、风险预警、推荐
- **效率（做）**：自动化重复动作——报价生成、信用审批、EoL

三类 benefit 对应"看 → 判断 → 做"的闭环，落到每个 persona 的工作流里。

### 3.5 EKP 作为 workspace 的知识底座（v6 新增）

交付层不是"6 个 persona 视图 + 6 个 Agent 调用"，还要有一个**知识底座**把每个 persona 的工作台填满。EKP 的四个能力直接对应交付层的四个动作：

| 交付层动作 | EKP 能力 | 具体怎么落地 |
|---|---|---|
| **Insight 推送** | 知识推荐（最新 / 热门 / 热门讨论 / 月度之星） | 新沉淀的服务产品知识、定价规则变更，主动推到对应 persona 工作台，而不是等业务人员来搜 |
| **Persona 个性化视图** | 我的空间（消息/订阅/收藏/关注） | 每个业务人员看自己订阅的知识域、收藏的 FAQ、关注的讨论——工作台不是通用聊天窗 |
| **L1 覆盖（AI 查知识）的数据来源** | 知识洞察（知识资产看板 + 消费洞察） | 只能度量 L1「AI 查知识」档（检索量、知识缺口）；L2–L4 的流程自动化覆盖需另用 workflow 执行日志度量 |
| **L1 覆盖（AI 查知识）的实现** | 知识检索（混合/全文/语义/多向量 + 深度检索） | 覆盖度里最基础的一档"AI 辅助人查知识"，就是 EKP 检索能力本身 |

**关键结论**：EKP 的"工作区（Workspace）"组织单元和本蓝图的"persona 化 workspace"是同一套逻辑——每个 persona 对应一个 EKP 工作区，拥有**独立的向量库、模型配置、检索策略**。这带来一个实际好处：SSG Pricing 的人搜"pen rate"不会命中 SSG Sales 的"客户异议话术"，角色之间知识天然隔离。

---

## 4. 三层架构

### 4.1 三层 + 知识底座

```
ISO Entry Layer（external）[复用：PIN / Sphere / Config AI+ / PAIDS / Aviso]
            ↓ interface
SSG Sales Workspace（交付层，服务 SSG 业务人员）[自建 B1]
    L0 编排 · 共享上下文 & Memory · 6 个 persona 视图
            ↓ 调用
6 个域 Agent（引擎层）[自建 B2：Agent 本体 + workflow]
    Service Product · Customer Engagement · Config & Quote ·
    Pricing · Sales Ops · Leasing
            ↓ MCP 调用
EKP 知识底座（贯穿交付层与引擎层）[复用]
    知识检索 · 知识本体 · 知识推荐 · Bad Case 闭环
   Skill Hub 能力封装 [复用]　　CPM / SPEP 可计算 [复用]
```

- **ISO Entry Layer**：SSG 作为整体对外的接口，ISO 通过它消费 SSG 的 AI 能力。
- **SSG Sales Workspace**：交付层，SSG 业务人员的工作台。
- **6 域 Agent**：引擎层，能力封装与执行。
- **EKP 知识底座**：v6 新增的横切层——向上给交付层供"知识推荐 / 个人空间 / 洞察"，向下给引擎层供"检索 / 本体"。

### 4.2 EKP 在三层架构中的位置（v6 新增）

EKP 不是三层之外的"第四层"，而是**横切的知识底座**，被交付层和引擎层同时消费：

- **交付层消费 EKP**：persona 工作台里的 Insight 推送（知识推荐）、个性化视图（我的空间）、L1 知识覆盖的数据（知识洞察）。
- **引擎层消费 EKP**：6 个域 Agent 通过 MCP 调 EKP 检索，取回"答案 + 来源"再加工。

这样设计的好处是**知识只沉淀一份**：Service Product 的知识在 EKP 里维护一次，Service Product Info Agent 检索它、Service Product Enablement team 的工作台也推送它，不会出现"Agent 内置一套知识、工作台又另存一套"的双份维护。

> **可行性前提已确认（2026-09）**：EKP 具备标准的对外 API 和 MCP——6 域 Agent 通过 MCP 实时调 EKP 检索这条链路成立，无需另做适配层。

### 4.3 Build vs Reuse 决策地图（v6 新增）

顶层设计的核心输出之一，是显式标出每一层「复用」还是「自建」。复用企业已有能力降低建设成本，自建项是方案的正当组成部分、纳入计划范围。

**从高到低完整映射**：

| 层 | 组件 | 复用（Leverage） | 自建（Build） |
|---|---|---|---|
| 愿景 | Northstar / AI 承诺 | — | — |
| 交付层 | persona 工作台 | EKP「我的空间」「知识推荐」 | **Workspace 交付层本体** |
| 交付层 | 覆盖度 L0–L4 | EKP 知识洞察（只填 L1） | **L2–L4 流程自动化度量** |
| 引擎层 | 6 域 Agent | EKP 检索、Skill Hub 封装、CPM/SPEP 可计算 | **6 个业务 Agent + workflow** |
| 协作层 | L0 编排 | MCP / A2A 协议标准 | **L0 编排器** |
| 协作层 | 共享上下文 | EKP 本体（schema 参考） | **运行时存储（DB + 事件总线）** |
| 质量层 | 质量门禁 | EKP Bad Case 闭环、5 级权限审计 | **LLM-as-judge + guardrail** |

**Build 清单（6 个自建项，纳入计划范围）**：

| # | 自建项 | 建设范围 | 优先级 | 复用/依赖 |
|---|---|---|---|---|
| B1 | Workspace 交付层 | persona 化工作台（把 6 Agent 编排成业务视图） | P0 | 复用 EKP 我的空间 / 知识推荐 |
| B2 | 6 域 Agent 本体 + workflow | 6 个业务 Agent 的推理逻辑 + 确定性流程 | P0 | 复用 EKP 检索、Skill Hub、CPM/SPEP |
| B3 | L0 编排器 | 多 Agent 任务分解 / 委派 / 结果合成 | P1 | 复用 MCP / A2A 协议 |
| B4 | 共享上下文运行时 | 高频事件/状态的存储（DB + 事件总线） | P1 | schema 参考 EKP 本体 |
| B5 | L2–L4 覆盖度度量 | workflow 执行日志采集 + 度量框架 | P0 | 复用 EKP 知识洞察（填 L1） |
| B6 | 质量门禁 | LLM-as-judge + guardrail 分离 + 评测集 | P1 | 复用 EKP Bad Case 闭环（知识质量） |

**关键结论**：方案不是"全部自己造"，也不是"全指望 EKP"。分工是——**知识交给 EKP、能力封装交给 Skill Hub、可计算交给业务系统、协议用开放标准；但交付层、Agent 本体、编排、运行时上下文、度量、门禁这 6 块是 SSG 自己的核心资产，必须自建**。

---

## 5. 6 域 Agent 引擎层

### 5.1 保留 blueprint 的 6 域划分

| 域 Agent | 能力 | Owner（GPS） |
|---|---|---|
| Service Product Info Agent | 产品知识、offering 资格 | Chen Yan |
| Customer Engagement Agent | 客户互动、异议处理、ROI | Howie Zhu |
| Service Config Agent | 报价、配置、GBB 推荐 | Hongfei |
| Pricing Support Agent | 定价、pen rate、特殊 bid | Hongfei |
| APoS Agent | 销售运营自动化 | Hiten |
| Leasing Agent（DWS） | 信用/AP/EoL | Danny |

### 5.2 workflow vs agent 区分（降低落地风险）

industry best practice（Anthropic、Copilot Studio 三 harness）强调：**不要一上来就上全自主 agent**。

- **确定性 workflow**（预定义代码路径）：报价生成、SKU 校验、邮件 intake → 用 workflow，可预测、低成本。
- **自主 agent**（动态决策）：定价推荐、deal 判断 → 用 agent，灵活但成本高、需 guardrail。

每个域能力先区分"确定性"还是"需推理"，能用 workflow 就不用 agent。

### 5.3 能力封装（对齐 Skill Hub）

ROI 计算、GBB 推荐、信用审批等能力封装为可复用资产，对齐联想已有 **Skill Hub**——避免"每个 Agent 各写一套"。

### 5.4 域 Agent 的知识调用链（v6 新增）

每个域 Agent 的"知识类能力"（产品知识、offering 资格、ROI 话术、pen rate 规则）不应内嵌在 Agent 里，而应**统一从 EKP 取**。调用链如下：

```
域 Agent（判断"要什么知识"）
    ↓ MCP
EKP 检索（混合/全文/语义/多向量召回）
    ↓
深度检索（意图识别 + 答案评估）—— 可选，质量优先场景
    ↓
返回"答案 + 来源 + 置信度"给 Agent
    ↓
Agent 用答案继续推理（如基于 pen rate 规则算报价）
```

**6 域的知识来源映射到 EKP 知识库**：

| 域 Agent | EKP 知识库（按业务域分类） |
|---|---|
| Service Product Info Agent | 产品知识库（offering 资格、产品规格） |
| Customer Engagement Agent | 营销/销售知识库（ROI 论证、异议处理话术） |
| Service Config Agent | 产品 + 配置知识库（GBB 推荐规则） |
| Pricing Support Agent | 定价知识库（pen rate、special bid 规则） |
| APoS Agent | 运营知识库（流程 SOP、审批规则） |
| Leasing Agent（DWS） | 法务/财务知识库（信用、EoL 政策） |

**关键结论**：Agent 的"智能"来自推理（引擎层），"知识"来自 EKP（底座）——两者解耦，知识更新不用改 Agent 代码，在 EKP 里改一次全链路生效。

> **边界（可行性收敛）**：EKP 只承载**陈述性知识**（产品规格、异议话术、SOP、政策）。**可计算知识**（pen rate 公式、报价计算链）不是文档、EKP 检索不出可执行的公式，Pricing Support / Service Config 两个域的可计算部分**走业务系统（CPM / SPEP），不进 EKP**。上表 6 域里，Service Product / Customer Engagement / APoS / Leasing 的「查知识」适用 EKP，Pricing / Config 的「算结果」接业务系统。

### 5.5 域 Agent 能力定义（v6 补强）

> 已补 3 域（基于项目沉淀），其余 3 域待业务输入。能力 = 能力项 + 权限分级（Auto / 半自动 / 审批后）。

#### Service Product Info Agent（基于 Sales Enablement Agent V1 的 product 部分）

| 能力 | 说明 | 权限 |
|---|---|---|
| PN 生命周期管理 | Create / Extend / End-of-Life 判断 | 审批后执行 |
| Service Tier 体系维护 | Tier 定义、归属、Sub-Tier 划分 | 审批后 |
| ODT 属性管理 | Warranty Term / Service Tier / Region 变更 | 半自动 |
| MT 公告捕获 | Machine Type 公告字段（target price / service tier）提取入库 | 自动 |
| Offering 资格判断 | 产品资格、region 可用性 | 自动（只读） |

#### Service Config Agent（Config & Quote，基于 ISG SSR）

| 能力 | 说明 | 权限 |
|---|---|---|
| 报价生成 | 配置 + 报价组合 | 半自动 |
| SKU / 配置校验 | 兼容性、region 可用性 | 自动 |
| GBB 推荐 | Good / Better / Best 三档（XGBoost softprob 多分类） | 自动（建议） |
| Catalog 过滤 | Region / Contract / Lifecycle / Price 业务护栏 | 自动 |

#### Pricing Support Agent（基于 Pen Rate 三步 + ISG Price Update 16 步）

| 能力 | 说明 | 权限 |
|---|---|---|
| Pen Rate 计算 | Brand Mapping → 5 维 Delegation → Adjustment | 半自动 |
| Special Bid 审批 | 特殊价格审批流程 | 审批后 |
| 价格更新 | 16 步（PN Listing → 定价维度 → 成本 → 计算 → 发布） | 审批后发布 |
| PFV 竞争分析 | 竞品价格对标 | 自动（只读） |

#### 待补 3 域（需业务输入）

| 域 | 缺的输入 |
|---|---|
| Customer Engagement | 异议类型 / ROI 论证流程 / Deal Intelligence 定义 |
| APoS | 运营自动化覆盖流程 / AP 含义 |
| Leasing | 信用 / AP / EoL 流程 / DWS 含义 |

---

## 6. L0 共享上下文 + 协作协议（方向 A/B）

### 6.1 协议分层：MCP + A2A

industry 已经把 Agent 通信标准化成两个互补协议（不二选一）：

- **MCP**（Agent ↔ 工具/系统）：6 个域 Agent 调用业务系统（ICP/SPEP/SCFE/CPM 等）的标准。**v6 补充：EKP 也作为一个 MCP server 暴露给所有域 Agent**——"调 EKP 检索"和"调 ICP 查数据"走同一条协议。
- **A2A**（Agent ↔ Agent）：跨域级联（如 Product→Config→Pricing）的标准，Google 发起、Linux Foundation 托管，Salesforce/SAP/微软参与。

**借鉴动作**：域 Agent 调系统对齐 MCP 思路；跨域级联对齐 A2A 思路，不做 bespoke 集成。

### 6.2 共享上下文的边界（Secure & Opaque）

L0 共享上下文存四类对象（blueprint Slide 27 已命名）：

- **Scores**（可能性/优先级）：special-bid 审批概率、attach 倾向、rework 风险
- **Events**（发生的事）：quote 创建/修订、special bid 提交、objection 记录
- **States**（当前状态）：opportunity 阶段、审批状态、报价有效期
- **Profiles**（关键事实）：客户装机量、partner 资质、区域规则

**关键边界（A2A 的 Secure & Opaque 原则）**：共享的是**结果与事件**，不是每个 Agent 的内部记忆/工具/专有逻辑。否则共享上下文退化成"各写各的日志"。

**补三样东西（方向 A 做实）**：
1. 数据 schema（四类对象的结构定义）
2. 更新机制（谁写、何时写、事件如何广播）
3. 读写权限边界（每个 Agent 能读什么、能写什么）

### 6.3 EKP 知识本体作为共享上下文的 schema 建模参考（v6 新增，收敛后）

上面"补三样东西"里的**第一样——数据 schema 的建模——可以参考 EKP 的知识本体（Ontology）来画**。注意：EKP 本体只做 **schema 建模参考**，不是共享上下文的**运行时存储**（高频读写的事件/状态要落在独立数据层 + 事件总线，不是知识图谱）：

- EKP 本体模块支持**实体（概念）/ 属性 / 关系**建模，还能从文本自动抽取、导入本体、生成图谱。
- 四类共享对象可以落到本体上：
  - **Profiles → 实体**：客户（属性=装机量）、Partner（属性=资质）是本体里的实体。
  - **States → 属性**：opportunity 的"阶段"、报价的"有效期"是实体的属性。
  - **Events → 关系**：quote 创建/修订是发生在 opportunity 实体上的事件。
  - **Scores → 属性（衍生值）**：special-bid 审批概率是 opportunity 的一个衍生属性。

**带来的好处**：6 个域 Agent 对"同一个客户 / 同一个 opportunity"有**统一的语义理解**——不是各自定义字段，而是共享一张图谱。跨域级联（Product→Config→Pricing）传递的不是散装 JSON，而是图上一个实体到另一个实体的关系。

> 两个边界（可行性收敛）：① EKP 本体是**静态知识图谱**，只用来定义 schema 和语义关系；**运行时存储**（opportunity 实时状态、报价有效期、事件流）落在**数据库 + 事件总线**，不是 EKP。② Agent 内部的推理记忆（prompt、工具、专有逻辑）仍不进共享上下文——两者不冲突。

### 6.4 四类共享对象 schema 骨架（v6 补强）

基于 blueprint Slide 27 命名 + ISG SSR 数据模型，给出四类对象的骨架定义（字段为骨架，落地时补全）：

| 对象 | 定义 | 骨架字段 | 谁写 | 谁读 |
|---|---|---|---|---|
| **Scores** | 可能性 / 优先级 | special-bid 审批概率、attach 倾向、GBB 推荐概率、rework 风险 | Pricing / Config Agent | 所有域 |
| **Events** | 发生的事 | quote 创建/修订、special bid 提交、PN 创建/关闭、MT 公告、objection 记录 | 各域 Agent | 编排器 + 相关域 |
| **States** | 当前状态 | opportunity 阶段、审批状态、报价有效期、PN 生命周期状态 | 各域 Agent | 所有域 |
| **Profiles** | 关键事实 | 客户装机量、partner 资质、区域规则、PN 属性（Tier/Warranty）、Service Tier 体系 | 主数据系统 + EKP | 所有域 |

> 读写边界沿用 §6.2 的 Secure & Opaque：共享「结果与事件」，不共享各 Agent 内部记忆。骨架字段待 3 个待补域（Customer Engagement / APoS / Leasing）输入后补全。

---

## 7. 评估与质量门禁（方向 C）

blueprint 有 4 层"上线后"指标，缺"上线前"评测。补齐如下：

### 7.1 上线前评测（小样本立即开始）

每个域 Agent 上线前配 **20 条真实业务场景评测集**（覆盖 4 焦点的典型用例），不要等凑齐几百条。评估"最终产出对不对"（报价对不对、推荐合不合理），而非"中间步骤"（end-state evaluation）。

### 7.2 LLM-as-judge + Human eval

- **LLM-as-judge**：按 rubric（事实准确 / 完整性 / 来源质量 / 工具效率）规模化打分，适合有明确答案的用例。
- **Human eval**：抓自动化之盲区（幻觉、护栏违规、边缘场景），必须保留人工抽检。

### 7.3 Guardrail 分离

guardrail 应是**独立的筛查层/实例**，不与业务 agent 耦合（Anthropic parallelization 模式）。关键产出（报价、定价推荐）加一个 evaluator 做上线前质检循环。

### 7.4 生产可靠性

6 域 Agent 上线需配套：可恢复状态（resume from checkpoint）、重试、灰度发布（rainbow deployment）、监控 agent 决策模式（非对话内容）的可观测性。

### 7.5 EKP Bad Case 闭环作为知识质量门禁（v6 新增）

7.1~7.4 解决"Agent 整体输出对不对"，但还有一类质量问题是"**知识检索对不对**"——Agent 推理没错，但取回的知识是错的/过时的。这类问题由 EKP 自带的 Bad Case 闭环承接：

```
用户搜索 → 评价反馈（已解答 / 部分解答 / 未解答）
  → 生成 Bad Case 用例
  → 根因分析（下拉选/手填）
  → 分派知识库（主用例 + 子用例独立状态）
  → 知识库优化处理
  → 复测验证（左右对比：原检索 vs 最新检索）
  → 完成/关闭闭环
```

**两个闭环的分工**（避免混淆）：

| 闭环 | 管什么 | 机制 | 周期 |
|---|---|---|---|
| 上线前评测（7.1） | Agent 整体输出对不对 | 20 条场景 + end-state eval | 上线前 + 每次大改 |
| EKP Bad Case 闭环（7.5） | 知识检索对不对、知识缺不缺 | 用户评价 → 根因 → 优化 → 复测 | 持续、线上滚动 |

**知识缺口驱动评测集扩充**：EKP 知识洞察里的"知识缺口指标"（某域检索量高但"未解答"多）就是评测集扩充的信号——缺口在哪，就在哪补知识 + 补评测用例，形成"评测 ← 缺口 ← 检索"的正向循环。

> 一句话：EKP 把"知识质量"这件事从 Agent 上线后的玄学，变成了一个有闭环、可复测、可追踪的工程过程。

---

## 8. 路径与投资（保留 blueprint + 补财务闭环）

### 8.1 12 Moves（保留）

4 焦点 × 3 财年（FY2627/2728/2829），每焦点 3 个 move 从痛点走到北极星。此部分沿用 blueprint Slide 12。

### 8.2 投资与财务闭环（补强）

- 现状：总 $2.74M，已批 $1.8M，缺口 $0.64M；多个项目 ROI "to be filled"。
- **补强**：建立"价值验证 → 追加投资"闭环。用 L0–L4 覆盖度 + 上线前评测 + Layer 3/4 KPI，形成每个财年的价值验证节点，作为追加投资的依据，而不是干等 business case review。

---

## 9. 治理与所有权

### 9.1 4 Workstream（保留 blueprint + 补缺口）

- W1 平台与架构（Hiten，存在）
- W2 域 Agent（domain owners，存在）
- **W3 数据与知识（UNASSIGNED，缺口）** → 需补 owner
- **W4 采纳与变革（UNASSIGNED，缺口）** → 需补 owner（industry 反复证明：采纳是 AI 项目失败头号原因）

> v6 补充：W3"数据与知识"的 owner，正好是 EKP 底座的第一责任人——他管的是知识本体的建模、知识库的维护、Bad Case 闭环的运转。EKP 的六大角色（工作区管理员/知识库所有者/知识运营员/标注员）就是这个 workstream 的落地班底。

### 9.2 双实例对齐（补强）

GPS 与 DWS/HC 共享模式，需补"实例间能力对齐/复用"约定，防两边各造各的轮子。

---

## 10. 下一步方向汇总（8 方向 + best practice 融入 + EKP 底座）

| 优先级 | 方向 | 融入动作 |
|---|---|---|
| P0 | Workspace 交付层 | 升级为角色化工作台，服务 SSG 业务人员 |
| P0 | 覆盖度度量 | L0–L4 分级，每个 persona 列工作清单 |
| P0 | 协议分层 | MCP（调系统 + 调 EKP）+ A2A（跨域协作） |
| P0 | **EKP 知识底座**（v6 新增） | 交付层消费知识推荐/洞察，引擎层消费检索/本体 |
| P1 | 多 Agent 编排 | L0 定义任务边界/输出格式/工具指引 |
| P1 | 共享上下文边界 | 只存结果与事件，Secure & Opaque；schema 用 EKP 本体 |
| P1 | 上线前评测 | 每 Agent 20 条场景评测集 + end-state |
| P1 | 质量门禁 | LLM-as-judge + human eval + guardrail 分离 + EKP Bad Case 闭环 |
| P2 | 确定性优先 | workflow vs agent 区分 |
| P2 | 生产可靠性 | resume/retry/灰度/observability |
| P2 | 三原则 | simplicity / transparency / ACI 写进设计原则 |

---

## 11. 待确认 / 待补信息

1. **Persona 的完整清单与边界**：SSG Sales / SSG Pricing / Service Product Enablement / Service Sales Ops / Leasing 这 5 个是否完整？是否还缺 SSG 内部其他角色（如服务产品经理、SSG 领导层）？
2. **覆盖度基线的现状值**：各 persona 当前处于 L0–L4 哪一级？需要各 domain owner 填。
3. **W3/W4 owner 人选**：顶层设计里列为缺口，需要你或 leadership 拍板。W3 尤其重要——它是 EKP 底座的第一责任人。
4. **$0.64M 缺口方案**：财务闭环的具体机制待定。
5. **（v6 新增）EKP 工作区与 persona 的映射确认**：是否每个 persona 独立建一个 EKP 工作区？还是先建一个 SSG 统一工作区、按知识库分区？这影响知识隔离粒度与运维成本，需与 EKP 平台团队对齐。
