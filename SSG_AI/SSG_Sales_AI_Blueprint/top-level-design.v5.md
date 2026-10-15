# SSG Sales AI 顶层设计

> 版本：v5（基于 Blueprint v4 前 30 页深化，融入 industry best practice 调研）
> 状态：概念与方向草案，待 review
> 调研支撑：`references/industry-best-practices.md`

---

## 0. 文档定位

本文档在 SSG Sales AI Blueprint v4 之上做两件事：

1. **补上缺失的"交付层"**——把 blueprint 的"6 域 Agent + 编排层"升级为"角色化 Workspace（交付层）+ 域 Agent（引擎层）"的完整架构。
2. **用 industry best practice 细化 8 个补强方向**——共享上下文、协作协议、评估门禁、覆盖度度量等，让顶层设计从"概念"走到"可落地的方向与设计"。

---

## 1. 定位与愿景

- **SSG Northstar**：Build and operate AI for the Modern Enterprise（为现代企业构建并运营 AI）。
- **本蓝图交付**：Inside Sales Transformation 的 AI 承诺（$1.8M 已批资金、30%→50% 流程自动化、SSIR 生产力 +15%、GPS MT $2.63B +17%）。
- **核心判断**（industry 共识，非口号）：AI in sales 已经不是一个"工具问题"，而是一个"基础设施问题"。Gartner 的失败模式警告——2028 年 Agent 数量是销售的 10 倍，却不到 40% 的人认可其生产力提升——本质是"没有共享上下文层 + 没有明确 owner"。

**因此，本蓝图的目标不是"多做几个 Agent"，而是"把 SSG 销售变成一个 AI-native 的整体"**。

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

**流程级覆盖度（补充）**：除了按 persona 工作清单度量，还需按**服务销售流程阶段**度量——opportunity → solution → 报价 → CPQ 各标 L0–L4。这度量的是「端到端哪几段 AI 覆盖、哪几段还是人工接力」，是服务销售总智能体（编排层）的价值证据，与 persona 工作覆盖度互补。

### 3.4 三类 Benefit 落到 persona（效率 / data / insight 闭环）

- **Data（看）**：统一数据模型上的自助查询、可视化
- **Insight（判断）**：主动推送——客户倾向、价格机会、风险预警、推荐
- **效率（做）**：自动化重复动作——报价生成、信用审批、EoL

三类 benefit 对应"看 → 判断 → 做"的闭环，落到每个 persona 的工作流里。

---

## 4. 三层架构

```
ISO Entry Layer（external）
    PIN / Sphere · Config AI+ · PAIDS · Aviso
            ↓ interface
SSG Sales Workspace（交付层，服务 SSG 业务人员）
    服务销售总智能体（编排）· 共享上下文 & Memory · 6 个 persona 视图
            ↓ 调用
6 个域 Agent（引擎层）
    Service Product · Customer Engagement · Config & Quote ·
    Pricing · Sales Ops · Leasing
```

- **ISO Entry Layer**：SSG 作为整体对外的接口，ISO 通过它消费 SSG 的 AI 能力。
- **SSG Sales Workspace**：交付层，SSG 业务人员的工作台。
- **6 域 Agent**：引擎层，能力封装与执行。

### 4.1 服务销售总智能体（编排层）

Workspace 里的「服务销售总智能体」不是新的 UI 层，而是**编排层**的具象化——把散点的域能力串成端到端流程。它活在 persona 工作台之下，用户感知不到独立界面。

- **定位**：编排层，不是新 UI。销售在 persona 工作台发起「服务销售流程」，总智能体在后台串起 opportunity → solution → 报价 → CPQ，结果落回各角色工作台。
- **scope**：3 个域——Service Product（服务介绍 / 支持范围）+ Config & Quote（推荐 / 配置 / 服务+硬件匹配）+ Pricing（报价）。Customer Engagement（异议 / ROI）不在 scope 内，由该域自己的流程处理。
- **命名边界**：它是「服务销售流程的编排器」，不是「6 域总编排」——未来其他流程（客户互动、销售运营）可能有各自的编排器。
- **协作顺序**：推荐先行、价格后置——推荐先出候选，定价再算价格，消除循环依赖。

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

---

## 6. L0 共享上下文 + 协作协议（方向 A/B）

### 6.1 协议分层：MCP + A2A

industry 已经把 Agent 通信标准化成两个互补协议（不二选一）：

- **MCP**（Agent ↔ 工具/系统）：6 个域 Agent 调用业务系统（ICP/SPEP/SCFE/CPM 等）的标准。
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

### 6.3 知识与数据的三层结构

「Unified Data & Knowledge」不是单一底座，而是三层：

| 层 | 内容 | 状态 |
|---|---|---|
| L1 infra | 数据湖、知识库、catalog、业务规则（EKP / ICP / SPEP / SCFE / CPM） | 已有 |
| L2 语义层 | ontology（本体）+ graph（图）+ 语义模型，把数据组织成业务本体 | 待建（自建 vs 复用 Fabric IQ 待决策） |
| L3 顾问 Agent | 封装「对话 + 洞察」的知识专家，能被自然语言问 | 待建 |

- **L1 是原料**，L3 顾问离不开 L1/L2，是 infra 之上的智能封装，不是替代。
- **两种访问模式并存**：域 Agent 直接调 L1（简单查询，MCP 查知识库）；或问 L3 顾问（复杂理解，自然语言得洞察）。
- **L2 待决策**：ontology/graph 自建（基于 EKP + BCPF）还是复用微软 Fabric IQ，取决于许可与合规。

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
- **W3 数据与知识（UNASSIGNED，缺口）** → 需补 owner（对应 §6.3 三层结构）
- **W4 采纳与变革（UNASSIGNED，缺口）** → 需补 owner（industry 反复证明：采纳是 AI 项目失败头号原因）
- **W5 安全合规（UNASSIGNED，缺口）** → 需补 owner（跨域共享的合规 / 数据主权）
- **W6 用户体验（UNASSIGNED，缺口）** → 需补 owner（跨 persona 的体验一致性）

> W3–W6 构成**横向支撑层**（数据知识 / 采纳变革 / 安全合规 / 用户体验），为多个域 Agent 与 persona 提供跨域支撑——对齐中国区擎天项目「跨项目支持团队」的分层思路。

### 9.2 双实例对齐（补强）

GPS 与 DWS/HC 共享模式，需补"实例间能力对齐/复用"约定，防两边各造各的轮子。

---

## 10. 下一步方向汇总（8 方向 + best practice 融入）

| 优先级 | 方向 | 融入动作 |
|---|---|---|
| P0 | Workspace 交付层 | 升级为角色化工作台，服务 SSG 业务人员 |
| P0 | 覆盖度度量 | L0–L4 分级，每个 persona 列工作清单 |
| P0 | 协议分层 | MCP（调系统）+ A2A（跨域协作） |
| P1 | 多 Agent 编排 | L0 定义任务边界/输出格式/工具指引 |
| P1 | 共享上下文边界 | 只存结果与事件，Secure & Opaque |
| P1 | 上线前评测 | 每 Agent 20 条场景评测集 + end-state |
| P1 | 质量门禁 | LLM-as-judge + human eval + guardrail 分离 |
| P2 | 确定性优先 | workflow vs agent 区分 |
| P2 | 生产可靠性 | resume/retry/灰度/observability |
| P2 | 三原则 | simplicity / transparency / ACI 写进设计原则 |

---

## 10.5 技术侧重点风险（业务侧概念已定，技术侧提高重视）

业务侧概念保持合理（不因当前技术未成熟而退缩），但技术落地时以下风险需重点盯：

| 风险 | 说明 | 缓解方向 |
|---|---|---|
| 多智能体编排 / 跨域调度 | supervisor 调度多个域 Agent 是业界公认难点（中国区擎天明示「未实现」） | 复用成熟编排平台（Vetra/DeerFlow 或微软 Copilot），不自建 supervisor |
| 跨域 A2A 协作的实时性与一致性 | 推荐↔定价↔配置的级联，结果确定性与状态连续性是关键 | 底层数据流保持（结构化传递）+ 上层顾问叙事；推荐先行价格后置 |
| 知识新鲜度的工程实现 | catalog / offering 资格 / 规则持续更新，跟不上会推荐过期服务 | L2 语义层的更新机制（谁写、何时写、如何广播） |

> 这三项不改变业务侧概念，但进入实施设计时需显式评估成熟度与降级方案。

---

## 11. 待确认 / 待补信息

1. **Persona 的完整清单与边界**：SSG Sales / SSG Pricing / Service Product Enablement / Service Sales Ops / Leasing 这 5 个是否完整？是否还缺 SSG 内部其他角色（如服务产品经理、SSG 领导层）？
2. **覆盖度基线的现状值**：各 persona 当前处于 L0–L4 哪一级？需要各 domain owner 填。
3. **W3/W4 owner 人选**：顶层设计里列为缺口，需要你或 leadership 拍板。
4. **$0.64M 缺口方案**：财务闭环的具体机制待定。
