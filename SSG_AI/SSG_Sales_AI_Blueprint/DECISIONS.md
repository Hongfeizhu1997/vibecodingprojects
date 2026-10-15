# Decisions — SSG Sales AI Blueprint（顶层设计）

> SSG AI 母舰级顶层设计持久化决策记录。只增不改。

---

## 2026-10-15 — 服务销售总智能体 = 编排层（并存，非替代）

- **Status**: Active
- **Context**: 顶层设计要支持「服务销售端到端流程」，是否新增「总智能体」层，与现有「按 persona 分工作台」是什么关系。
- **Decision**: **并存**——总智能体 = 编排层（Workspace 里 L0 编排的具象化），persona 工作台 = 交付层。总智能体不是新 UI，活在 persona 工作台之下，串起 opportunity → solution → 报价 → CPQ。
- **Consequence**:
  - 总智能体是「服务销售流程的编排器」，不是「6 域总编排」
  - 销售在 persona 工作台发起流程，总智能体后台串，结果落回各角色工作台
  - 保留 Persona-based 原则（各角色专业视图不被通用入口取代）

---

## 2026-10-15 — 服务销售总智能体 scope = 3 域

- **Status**: Active
- **Context**: 服务销售流程（opportunity → CPQ）需要哪些域能力？Customer Engagement 进不进？
- **Decision**: scope = **3 域**——Service Product（介绍 / 支持范围）+ Config & Quote（推荐 / 配置 / 匹配）+ Pricing（报价）。Customer Engagement（异议 / ROI）不进，由该域自己的流程处理。
- **Consequence**:
  - 总智能体边界清晰，不变成「销售大杂烩」
  - Customer Engagement 域独立演进，未来若需跨域协作再议

---

## 2026-10-15 — 推荐↔定价协作顺序：推荐先行、价格后置

- **Status**: Active
- **Context**: 推荐依赖定价（价格不合适不推）、定价依赖推荐（先有推荐才有定价对象），存在循环依赖。
- **Decision**: **推荐先行、价格后置**——推荐先出候选，定价再算价格，推荐在价格带内收敛。
- **Consequence**:
  - 消除死锁 / 无限循环风险
  - 底层数据流（结构化传递）保持确定性，上层顾问叙事作为业务表达，二者并存

---

## 2026-10-15 — 知识与数据三层结构（L1 infra + L2 语义 + L3 顾问）

- **Status**: Active（L2 自建 vs 复用 Fabric IQ **待决策**）
- **Context**: 「Unified Data & Knowledge」是单一底座，还是分层？专家顾问 Agent 是否需要 infra 支撑？
- **Decision**: 三层——**L1 infra**（数据湖 / 知识库 / catalog / 规则，已有）+ **L2 语义层**（ontology + graph + 语义模型，待建）+ **L3 顾问 Agent**（对话 + 洞察，待建）。L3 是 infra 之上的智能封装，不是替代。
- **Consequence**:
  - L1 复用 EKP / catalog 等已有系统
  - L2 语义层「自建 vs 复用微软 Fabric IQ」待决策（取决于许可与合规）
  - 两种访问模式并存：域 Agent 直接调 L1（简单查询）或问 L3 顾问（复杂理解）
