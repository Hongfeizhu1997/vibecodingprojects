# SSG Sales AI 顶层设计 — Industry Best Practice 调研支撑

> 用途：为 SSG Sales AI 顶层设计的完善与细化提供行业最佳实践依据。
> 来源：Anthropic（Building Effective Agents / Multi-Agent Research System）、MCP / A2A 协议、Salesforce Agentforce、Microsoft Copilot Studio 官方文档；结合内部 iChain Persona Workspace、SupplyX Workspace、VetraFlow 沉淀。
> 采集日期：2026-09。原始抓取文本见 `references/scrape/`。

---

## 一、Workspace / 交付层设计（本任务核心）

### 1.1 行业共识：从"多点 Agent"到"角色化工作台"

三股信号汇聚到同一个结论——Agent 的价值不在"Agent 本身"，而在"它如何被组织成业务人员可持续消费的工作面"：

- **Salesforce Agentforce** 的定位语是 "Humans with Agents drive customer success together"——强调人类 + Agent 协同，不是 Agent 替代人，也不是散点 Agent。产品面是一个统一的工作台（Agentforce Builder / Voice / Operations / AgentExchange），而不是一堆独立 Agent。
- **Microsoft Copilot Studio** 把 agent 与 workflow 放在同一个 studio 里，明确 "workflow can call an agent to complete a step"、agent 之间 "hand off"——交付的是**可编排的业务解决方案**，不是孤立的问答机器人。
- **内部 SupplyX 方向**（Robin 提案）：交付从"单点 Agent"转向"工作台/工作系统"——Agent 做出来之后要回答"用户在哪持续用、怎么用"，Workspace 是把"能力"变成"可被持续消费"的交付面。

**对 SSG 蓝图的借鉴**：现有蓝图是"6 个域 Agent + 一个编排层"，缺真正的交付面。应把 `SSG Sales Workspace` 从编排层升级为**交付层**——业务人员的入口、按角色组织、覆盖其全部工作内容。

### 1.2 Persona 划分（角色化，而非功能模块化）

- **内部 iChain Persona Workspace**：明确 "Persona-based：每个角色一个专属工作台，不是通用聊天窗口"。三阶段演进 Human with AI Assistant → Human with Agent Teammate → Human-Agent Team；闭环 "Insight → Decision → Action"。
- 行业通用做法：按**角色（role/persona）**组织工作台，而非按功能模块。Salesforce 的 Sales Agents、Copilot 的三种 harness，本质都是"谁在用、干什么活"来切。

**对 SSG 蓝图的借鉴**：6 个域 Agent 按"能力域"切（报价/定价/运营/产品知识），但业务人员工作天然跨域。应在交付层按 **Persona**（seller / 定价专员 / 配置专员 / 服务产品经理 / APoS·Leasing 运营）组织，域 Agent 退到引擎层被 persona 按需调用。

### 1.3 工作覆盖度度量（把"覆盖"变成可管理对象）

- **内部 SupplyX**：L0–L4 覆盖分级把"AI 覆盖了员工多少工作"变成可管理的对象，比"准确率/Token/登录数"更能让业务和管理层看懂价值。
- 呼应已有原则：分布对比 > 抽象准确率。

**对 SSG 蓝图的借鉴**：为每个 persona 列工作清单，标注"AI 已覆盖 / 部分覆盖 / 未覆盖"，形成覆盖度分级。这既是设计目标，也是给管理层看的价值证明。

### 1.4 引擎层 vs 交付层分层

- **内部 SupplyX 方向 5**：Harness/VetraFlow = 引擎层（Agent 怎么跑、编排/记忆/约束/隔离）；Workspace = 交付层（能力怎么被组织/消费/度量/治理）。二者是"交付层调用引擎层"，不重叠。
- **Anthropic** 的 workflow vs agent 区分，是同一思想在更细粒度的体现：workflow = 预定义代码路径（可预测），agent = 动态自主决策（灵活）。行业共识是**不要一上来就上全自主 agent**，能走确定性 workflow 就走 workflow。

**对 SSG 蓝图的借鉴**：明确分层——6 域 Agent 是引擎层能力，Workspace 是交付层，二者分层不冲突。单个能力内部，先区分"确定性 workflow（如报价生成流水线）" vs "自主 agent（如自主定价）"，能用 workflow 就不用 agent。

### 1.5 三种 harness 的启示（Copilot Studio）

Copilot Studio 用三种 harness 覆盖不同场景，是一个可复用的分类框架：

| Harness | 定位 | 适用 |
|---|---|---|
| GitHub Copilot harness | reasoning-heavy、multistep、能自主分解 | 复杂多步流程（信用审批、合同） |
| Standard harness | rule-based、可预测、结构化对话 | 帮助台、信息查询、FAQ |
| Copilot chat harness | 知识优先、扩展已有 Copilot | 内部知识问答、政策 FAQ |

**对 SSG 蓝图的借鉴**：域内能力不必都是"自主 agent"。报价生成、SKU 校验这类可预测流程用 deterministic workflow；定价推荐、deal 判断这类需要推理的才用 agent。这直接降低落地风险与成本。

---

## 二、共享上下文层 + Agent 协作（方向 A/B）

### 2.1 协议分层：MCP（Agent↔Tool）+ A2A（Agent↔Agent）

行业已经把 Agent 的两类通信标准化成两个互补协议，**不是二选一**：

- **MCP**（Model Context Protocol）：agent 连接外部系统/工具/数据源的标准（"AI 应用的 USB-C 口"）。解决"一个 agent 怎么调用 6 个系统"。
- **A2A**（Agent2Agent Protocol）：agent 之间通信、委派、交换结果的标准。由 Google 发起、捐给 Linux Foundation，AWS/Cisco/IBM/Microsoft/Salesforce/SAP/ServiceNow 共同维护。
- 官方明确分工：**MCP 装备单个 agent 的工具；A2A 让 agent 之间安全协作**。

**对 SSG 蓝图的借鉴**：这是方向 B 的现成答案——6 个域 Agent 之间的跨域级联（Slide 27 的四个 cascade），不应每次 bespoke 集成，而应约定一套 Agent 间协作协议（对齐 A2A 思路）。Agent 调用 6 个业务系统（ICP/SPEP/SCFE/CPM 等），对齐 MCP 思路。

### 2.2 多 Agent 编排：orchestrator-worker 模式

- **Anthropic 多 Agent 研究系统**：lead agent 拆解任务 → spawn 并行 subagent → 合成结果。好处是 parallelization + separation of concerns + compression；代价是 token 消耗约 15×、协调复杂度上升。
- 关键原则 "**Teach the orchestrator how to delegate**"：每个 subagent 需要明确 objective、output format、工具/来源指引、任务边界，否则会重复劳动或留缺口。
- 适用边界：多 agent 适合"高价值 + 重并行 + 信息超单上下文窗口"的任务；不是所有场景都适合拆多 agent。

**对 SSG 蓝图的借鉴**：L0 编排层就是 orchestrator。关键不是"有几个 agent"，而是 orchestrator 如何给每个域 Agent 下发**明确的任务边界 + 输出格式 + 工具指引**。跨域级联应显式定义分工，而非让 agent 自由发挥。

### 2.3 共享上下文的边界（Secure & Opaque）

- **A2A 的 "Secure & Opaque" 原则**：agents 协作时**不需要共享内部 memory、工具或专有逻辑**——这既保安全也保知识产权。
- **Anthropic**：多 agent 通过独立 context window 实现 separation of concerns；需要持久化的共享状态走外部 memory（如把 plan 存到 Memory 避免上下文截断丢失）。

**对 SSG 蓝图的借鉴**：方向 A 的"L0 共享上下文层"要明确**边界**——存什么（Scores/Events/States/Profiles 四类，Slide 27 已命名）、谁可读写什么。核心洞察：共享的是**结果与事件**，不是每个 Agent 的内部状态/记忆。否则共享上下文退化成"各写各的日志"。

---

## 三、评估与质量门禁（方向 C）

### 3.1 上线前评测：从小样本立即开始

- **Anthropic 核心主张**："Start evaluating immediately with small samples"——不要等凑齐几百条评测集才评估。早期 prompt 改动效果巨大（30%→80%），20 条真实场景用例就能看出差异。
- 对 mutate state 的多轮 agent，用 **end-state evaluation**（评估最终状态对不对，而非每一步过程），并拆成离散 checkpoint。

**对 SSG 蓝图的借鉴**：每个域 Agent 上线前配 20 条左右的真实业务场景评测集（覆盖 4 焦点的典型用例），而不是等大规模 benchmark。评估"最终产出对不对"（报价对不对、推荐合不合理），而非"中间步骤"。

### 3.2 LLM-as-judge + rubric

- **Anthropic 实践**：用 LLM judge 按 rubric 打分（0.0–1.0 + pass/fail），维度如 factual accuracy / completeness / source quality / tool efficiency。单一 LLM 调用 + 单一 prompt 最一致。适合有明确答案的用例直接判对错。
- **Human eval 补自动化之盲区**：人会抓出幻觉答案、系统失败、来源选择偏差（如早期 agent 偏好 SEO 内容农场而非权威来源）。

**对 SSG 蓝图的借鉴**：报价正确性、推荐合理性能用 LLM-as-judge 规模化评估；但"幻觉、护栏违规、边缘场景"必须保留人工抽检。两类都要有。

### 3.3 Guardrails + evaluator-optimizer

- **Anthropic 的 parallelization 模式**明确举了 guardrail 例子：一个模型实例处理用户请求，另一个实例筛查不当内容——**分离 guardrail 与核心响应**，比让同一个 LLM 同时干两件事效果好。
- **evaluator-optimizer 模式**：一个 LLM 生成、另一个评估并反馈，循环优化。适合"有清晰评估标准 + 迭代改进有可测价值"的场景。

**对 SSG 蓝图的借鉴**：guardrail 应是**独立的筛查层/实例**，不与业务 agent 耦合。关键产出（报价、定价推荐）可加一个 evaluator 做上线前质检循环。

### 3.4 生产可靠性

- **Anthropic 教训**：agents are stateful、errors compound；无法简单重启，需要 resume-from-checkpoint、retry、rainbow deployment（灰度切流，避免打断运行中的 agent）；observability 要监控"决策模式与交互结构"而非对话内容（保隐私）。

**对 SSG 蓝图的借鉴**：6 个域 Agent 上线需要：可恢复的状态、重试、灰度发布、以及监控 agent 决策模式（不是对话内容）的可观测性。

---

## 四、核心设计原则（Anthropic 三原则，贯穿全文）

1. **Maintain simplicity**：从简单开始，只在复杂度可证明地带来改善时才加。能用单 LLM + retrieval 解决就不用多 agent。
2. **Prioritize transparency**：显式展示 agent 的 planning 步骤（让用户看得懂 agent 在想什么）。
3. **Carefully craft the ACI**（agent-computer interface）：tool 的定义和文档要像设计人机界面（HCI）一样用心——清晰、带示例、防呆（poka-yoke）。

**对 SSG 蓝图的借鉴**：这三点应写进顶层设计的设计原则——简单优先、可解释、工具接口精心设计。尤其是 transparency，直接支撑蓝图的"人机协同、可解释"诉求。

---

## 五、可借鉴点汇总（按优先级）

| 优先级 | 方向 | 核心 best practice | 融入蓝图的动作 |
|---|---|---|---|
| P0 | Workspace 交付层 | 引擎层/交付层分层；persona 组织 | 把 SSG Sales Workspace 升级为角色化交付层，域 Agent 退为引擎层 |
| P0 | 覆盖度度量 | L0–L4 覆盖分级 | 每个 persona 列工作清单 + 覆盖度标注 |
| P0 | 协议分层 | MCP + A2A 分工 | 域 Agent 调系统用 MCP 思路；跨域协作用 A2A 思路 |
| P1 | 多 Agent 编排 | orchestrator-worker + 明确分工 | L0 编排层定义任务边界/输出格式/工具指引 |
| P1 | 共享上下文边界 | Secure & Opaque | L0 只存结果与事件，不存各 Agent 内部状态 |
| P1 | 上线前评测 | 小样本立即开始 + end-state | 每 Agent 20 条场景评测集 |
| P1 | 质量门禁 | LLM-as-judge + human eval + guardrail 分离 | evaluator 质检循环 + 独立 guardrail 层 |
| P2 | 确定性优先 | workflow vs agent 区分 | 可预测流程用 workflow，推理场景才用 agent |
| P2 | 生产可靠性 | resume/retry/灰度/observability | 上线配套工程机制 |
| P2 | 三原则 | simplicity / transparency / ACI | 写进设计原则 |
