# SSG Sales Enablement Agent — 架构方案 V1

> 创建：2026-06-03 | 更新：2026-07-17 | 来源：iChain Persona Workspace + Vetra (VetraFlow) 平台 + SSG GPS 业务需求 + ITshare Engineering & AI Workshop (2026 May) + NextOra SW Dev Agent Phase1 方案 + ISG Price Update 16 步流程

---

## 1. 设计理念

**一句话**：为 SSG GPS 每个角色构建 Persona Agent，覆盖服务 PN 从创建到退出的全生命周期。

借鉴 iChain 三层模型：`Persona Workspace → Persona Agent → Execution Loop`，技术底座用 Vetra (VetraFlow) 平台（基于 DeerFlow 框架）+ Lenovo Hybrid AI Platform。

### Harness Engineering 定位

本架构遵循 **Harness Engineering** 范式。AI Config 团队在联想内部的演进路径为：

```
Prompt Engineering  →  Context Engineering  →  Harness Engineering
   (早期 POC)              (中期规模化)            (目标：自主 Agent 体系)
```

SSG Enablement Agent 直接以 Harness Engineering 为起点构建，核心理念与 AI Config 2.0 愿景一致：

> **Human sets objectives & boundaries + Agent autonomously plans & executes + Skill serves as reusable biz capabilities**

具体映射：

| Harness Engineering 原则 | 本方案实现 |
|--------------------------|-----------|
| Human sets objectives & boundaries | Safety Layer（Auto Execute / Approval Gate）划定操作边界 |
| Agent autonomously plans & executes | Master Agent 意图识别→任务拆解→Sub-Agent 并行执行 |
| Skill as reusable biz capabilities | 5 个 Sub-Agent 的能力以 Skill 形式封装，可插拔、可独立演进 |
| Harness as guardrail | 审批路由 + Audit Log 贯穿全流程，确保 Agent 在边界内行动 |

---

## 2. 架构总览

```
┌───────────────────────────────────────────────────────────┐
│                    CHANNEL LAYER（全渠道）                   │
│  ┌──────────┐  ┌──────────────────┐  ┌─────────────────┐  │
│  │ Teams Bot│  │ Web Persona      │  │ Embedded Widget │  │
│  │          │  │ Workspace        │  │ (SPEP/CPM 内嵌) │  │
│  └────┬─────┘  └────────┬─────────┘  └────────┬────────┘  │
│       │                 │                     │           │
├───────┴─────────────────┴─────────────────────┴───────────┤
│                 PERSONA WORKSPACE LAYER                     │
│  ┌──────────────┐ ┌──────────────┐ ┌────────────────────┐  │
│  │ GPS PM       │ │ Sales Enable │ │ Pricing            │  │
│  │ Workspace    │ │ Workspace    │ │ Workspace          │  │
│  │ • PN 创建    │ │ • Sales Cost │ │ • PFV 对标         │  │
│  │ • 生命周期   │ │ • 审批发布   │ │ • 定价计算         │  │
│  └──────┬───────┘ └──────┬───────┘ └────────┬───────────┘  │
├─────────┴────────────────┴──────────────────┴─────────────┤
│                  PERSONA AGENT LAYER（DeerFlow）             │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   MASTER AGENT                       │   │
│  │         意图识别 · 任务拆解 · 审批路由 · 结果汇总      │   │
│  └───┬─────────┬─────────┬─────────┬──────────┬────────┘   │
│  │         │         │         │          │             │
│  │  ┌───┴──┐ ┌───┴──┐ ┌───┴──┐ ┌───┴───┐                  │
│  │  │Price │ │Cost  │ │PN    │ │Life-  │                  │
│  │  │Agent │ │Agent │ │Agent │ │cycle  │                  │
│  │  │      │ │      │ │      │ │Agent  │                  │
│  │  └──┬───┘ └──┬───┘ └──┬───┘ └──┬────┘                  │
│  │     │        │        │        │                        │
├─────┴────────┴────────┴────────┴───────────────────────────┤
│                 SHARED KNOWLEDGE PIPELINE (RAG)              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  PN 流程 · Service Tier 规则 · 审批规则 · PFV 竞品数据 │  │
│  │  ODT 属性定义 · MT 字段 · Booking 脱敏规则 · 风险映射 │  │
│  └──────────────────────────────────────────────────────┘  │
├────────────────────────────────────────────────────────────┤
│                   SECURITY LAYER                           │
│  ┌──────────────────┐    ┌──────────────────────┐        │
│  │ AUTO EXECUTE     │    │ APPROVAL GATE        │        │
│  │ • 查询/检查/报告 │    │ • 成本/价格操作      │        │
│  │ • Agent 自主执行 │    │ • 需人审批后执行     │        │
│  └──────────────────┘    └──────────────────────┘        │
│  ┌──────────────────────────────────────────────────┐    │
│  │ AUDIT LOG（全操作可追溯）                          │    │
│  └──────────────────────────────────────────────────┘    │
├───────────────────────────────────────────────────────────┤
│                 INTEGRATION LAYER（MCP/Toolcall）          │
│  [ 渐进式披露：按任务上下文动态暴露工具，避免 prompt 膨胀 ] │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐  │
│  │ ICP  │ │ SPEP │ │ SCFE │ │ CPM  │ │ ODT  │ │Concord│  │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘  │
├───────────────────────────────────────────────────────────┤
│                 INFRASTRUCTURE                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Lenovo Hybrid AI Platform                         │   │
│  │  Models (SaaS LLM) / Knowledge (RAG) / Data / Tools│   │
│  └────────────────────────────────────────────────────┘   │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Vetra (VetraFlow) — 基于 DeerFlow 框架              │   │
│  │  Memory · Skills · Constraints · Sandbox              │   │
│  └────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────┘
```

### Vetra 2.0 核心组件与 SSG 架构映射

Vetra 平台定义四大核心组件，SSG 架构的各层直接对其映射：

| Vetra 2.0 组件 | 职责 | SSG 架构对应层 |
|---------------|------|---------------|
| **Memory** | 跨会话状态、经验、知识连续性 | §7 Memory System（短期/长期/领域记忆） |
| **Skills** | 可复用能力封装，独立版本化与测试 | Sub-Agent 能力以 Skill 形式封装，可插拔、可独立演进 |
| **Constraints** | 规则、权限、边界——确保 Agent 在受控范围内行动 | §5 Security Layer（Auto/Approval 分级 + Audit Log） |
| **Sandbox** | 隔离执行环境，安全验证代码与操作 | Integration Layer 中的所有系统调用均在沙箱内执行 |

> 注：DeerFlow 是字节跳动开源的多 Agent 编排框架（MIT 许可），Vetra 是联想基于 DeerFlow 构建的公司级 Agent 编排平台。关系类似于「Docker 是容器引擎，Kubernetes 是编排平台」——DeerFlow 提供 Sub-Agent 调度/编排原语，Vetra 在其上叠加企业级治理（Memory / Skills / Constraints / Sandbox）。

---

## 3. 角色与 Persona Agent 映射

| 角色 | 主要场景 | 对应 Sub-Agent | Workspace 焦点 |
|------|---------|---------------|---------------|
| **Pricing Team** | 16 步 ISG Price Update 全流程：PN 清单 → 定价维度映射 → 成本/汇率/折扣聚合 → 价格计算 → 审批发布 | Price Agent + Cost Agent + PN Agent（共享 Knowledge Pipeline） | 定价工作台：从原始 PN 列表到最终售价的全链路 |
| **Sales Enablement** | Sales Cost 计算、验证、发布 | Cost Agent | Cost 数据面板、审批 |
| **Finance Team** | 标准成本计算 | Cost Agent | 成本数据输入 |
| **GPS PM** | PN 创建、生命周期管理 | PN Agent, Lifecycle Agent | PN 创建视图、审批队列 |
| **TMO/SMO/SA** | PN 需求提交 | PN Agent（共享 Knowledge Pipeline） | 需求提交 + 流程指南 |
| **Offering Mgr / Portfolio Lead** | PN 报告查询 | Knowledge Pipeline（RAG 直接查询） | 客制化报告 |

---

## 4. Sub-Agent 能力矩阵

> **Skill-as-Product 原则**：每个 Sub-Agent 的能力以 Skill 形式封装，遵循独立版本化和独立测试策略。Skill = `prompts` + `tools` + `knowledge` + `tests` 四位一体，可插拔、可独立升级，不相互耦合。新增或修改一个 Skill 不影响其他 Agent 运行。

### 4.1 Price Agent（定价 — ISG Price Update 16 步核心）

> 基于 ISG Price Update 端到端流程（16 步）扩展。Price Agent 承担从定价维度定义到最终价格产出的完整链路，是 ISG 流程中覆盖步数最多（7/16 步）的 Sub-Agent。

| ISG 步骤 | 场景 | 能力 | 权限 |
|:--:|------|------|------|
| **5** | Pricing Dimensions Mapping | 定义每个 PN 的定价维度（GEO × 客户段 × Charge Type × Term），形成标准化定价模板 | **自动**（配置类，只写模板） |
| **5-** | Charge Type 匹配 | PN → CBSO Charge Type 自动映射，基于 ICP 字段匹配规则 | **自动**（基于规则） |
| **8** | Brand Mapping → DP | 品牌到 Deal Price 的映射关系维护、查询和异常检测 | **审批后更新** |
| **10** | #10 PFV 分析 | 自动抓取行业/竞品价格 → 生成对标报告 | **自动**（只读研究） |
| **11** | List Price Pull（CPM） | 从 CPM 拉取当前 List Price / Channel Price，校验字段完整性 | **自动**（只读） |
| **13** | Forex Translation | 多 GEO 汇率自动换算，按发布周期刷新汇率表 | **自动** |
| **14** | PN → CBSO 转换 | 服务 PN 到 CBSO 计费结构的自动转换，输出可比对的价格基准 | **自动**（可人工校验） |
| **15** | #11 Price Calc & Shaping | 综合 Std Cost + PFV + Channel Discount + Forex → 生成推荐售价，标注置信度 | **审批后发布** |

### 4.2 Cost Agent（成本管理）

> 扩展后覆盖 ISG Price Update 流程中的成本拉取、渠道折扣管理和 HW/Warranty 数据接入。

| ISG 步骤 | 场景 | 能力 | 权限 |
|:--:|------|------|------|
| **12** | #8 标准成本计算 | 从 SCFE 取 PH3 数据 → 加权平均计算 → 展示 | **审批后写入** |
| — | #9 Sales Cost Uplift | 分析历史 uplift 规则 → 建议规则和数值 | **审批后写入 CPM** |
| **9** | Channel Discount 管理 | 渠道折扣规则查询和数值维护，按 GEO/渠道/客户段分层 | **审批后写入 CPM** |
| **4,6** | HW / EOS 数据接入 | ICP HW Master Data + EOS HW Listing 作为成本计算的硬件侧输入 | **自动**（只读） |
| — | Sales Cost 验证 | 对标 HW AUR → 完整性检查 → 报告异常 | **自动**（只读） |

### 4.3 PN Agent（PN 全生命周期）

| ISG 步骤 | 场景 | 能力 | 权限 |
|:--:|------|------|------|
| — | #2 自动生成 POR/表单 | 接收需求信息 → 调 SPEP API 生成 | **自动** |
| — | #3 重复检查 | PN 编号/属性 → 调 SPEP 查重 → 返回建议 | **自动** |
| — | #7 创建/扩展判断 | 分析 MT 归属 → 建议 extend 或 create new | **半自动**（涉及新 PN Portfolio 创建需审批） |
| **1-4,10** | **PN Listing & Finalize** | 拉取 Published / Not-published PN 列表 + PN Master + HW-PN Compatibility → 综合筛选生成最终定价 PN 清单 | **审批后锁定** |

> ⚠️ **优先级调整 (2026-07-09)**：PN Agent 从 Wave 2 后移至 Wave 3。PN 团队当前已在使用 Spark / Copilot / Web Coding 等 AI 工具覆盖重复性编码和表单生成场景，本阶段聚焦团队尚未覆盖的决策辅助与生命周期管理，不重复建设已有能力。
> 
> **ISG 流程新增 (2026-07-17)**：PN Agent 新增「PN Listing & Finalize」能力——ISG Price Update 的前 4 步（PN 列表拉取 + 兼容性校验 + 清单锁定）是定价流程的前置输入，PN Agent 负责确保进入定价环节的 PN 清单完整且无遗漏。

### 4.4 Lifecycle Agent（生命周期管理）
| 场景 | 能力 | 权限 |
|------|------|------|
| #5 PN 定期清理 | 按规则扫描 → 筛选可关闭 PN → 生成审核列表 | **自动筛选** |
| PN 关闭审批 | 发送审批请求 → 收集各 Geo 反馈 → 汇总 | **半自动**（审批后执行关闭） |

### 4.5 RAG Knowledge Pipeline（共享知识管线）

> ⚠️ **设计修正 (2026-06-18)**：RAG 知识管线是共享基础设施，不是与 PN/Cost/Price/Lifecycle Agent 同级对等的 Sub-Agent。所有 Sub-Agent 通过工具调用访问 RAG，而不是由 Master Agent 路由到一个独立的 "Knowledge Agent"。

**定位**：所有 Sub-Agent 的底层共享能力，类似数据库或文件系统——任何时候 Sub-Agent 需要查询 PN 流程规则、Service Tier 定义、审批矩阵、MT 字段定义等信息时，直接调用 RAG 管线，不需要通过另一个 Agent。

**为什么不做成独立 Sub-Agent**：
- 知识和操作不在同一层级：一个 Agent "知道规则" 和 "执行操作" 是两种不同能力，混淆会模糊架构边界
- 每次知识查询 → Agent → Agent 的调用链增加延迟
- 直接作为共享工具集更简洁：Sub-Agent 调 `query_rag(query)` 就像调 `query_db(sql)` 一样直接

**知识架构：Hybrid RAG + PageIndex**

纯语义 RAG（chunk + embedding retrieval）在 SSG 场景中存在三个缺陷：

| 问题 | 说明 | SSG 示例 |
|------|------|---------|
| **上下文分裂** | 依赖关系跨 chunk 断裂，语义检索无法还原完整推理链 | PN 生命周期规则 "A→B→C" 被切成 3 个 chunk，检索只返回 B |
| **路径不透明** | 检索到的上下文来源路径不可追踪，无法验证信息权威性 | 审批规则版本 v2 和 v3 未区分，Agent 用了过期规则 |
| **输出不稳定** | 同一问题的向量召回结果随 embedding 浮动，答案不一致 | 两次问 "Warranty 变更审批流程"，返回结果不同 |

因此采用 **Hybrid RAG + PageIndex** 双层知识架构：

```
┌─────────────────────────────────────────────────┐
│              Hybrid 知识架构                      │
│                                                  │
│  PageIndex（结构化检索）          RAG（语义补充）  │
│  ┌─────────────────────┐    ┌─────────────────┐  │
│  │ 按领域组织层次路径    │    │ chunk + embedding│  │
│  │ 完整推理上下文加载    │    │ 补充细节粒度检索  │  │
│  │ 路径可追踪、输出稳定  │    │ 覆盖非结构化内容  │  │
│  └─────────────────────┘    └─────────────────┘  │
│         ↓                          ↓             │
│   权威规则/流程/          非结构化文档/           │
│   审批矩阵/字段定义        历史经验/FAQ           │
└─────────────────────────────────────────────────┘
```

- **PageIndex**：对 PN 生命周期规则、Service Tier 定义、审批矩阵、ODT 字段定义等**结构化权威知识**，按领域建层次化页面索引，Agent 决策时加载完整上下文而非碎片 chunk
- **RAG**：对 MT 公告历史、PFV 竞品报告等**非结构化增量内容**，用语义检索补充细节，兼顾覆盖广度

**能力清单**：

| 能力 | 说明 | 调用方 |
|------|------|--------|
| PN 生命周期规则检索 | Create/Extend/End-of-Life 判断条件 | PN Agent, Lifecycle Agent |
| Service Tier 体系查询 | Tier 定义、归属规则、Sub-Tier 划分 | PN Agent, Price Agent |
| 审批规则查询 | 哪些操作需要哪级审批、审批人 | 所有 Sub-Agent |
| ODT 属性字段定义 | 每个属性的含义、影响维度、变更映射 | PN Agent, Lifecycle Agent |
| MT Announcement 字段解析 | 公告字段定义、结构化提取模板 | RAG（定时任务自动消费） |
| PFV 竞品数据检索 | 行业价格、竞品对标信息 | Price Agent |
| 风险映射表 | 变更类型 → 风险等级 | RAG（影响分析时自动消费） |
| Booking 数据脱敏规则 | 哪些字段不能直接展示 | 所有 Sub-Agent |

**在 Wave 1 中的特殊角色**：

Wave 1 没有 PN/Cost/Price/Lifecycle Agent，只有查询场景。此时 RAG Knowledge Pipeline 通过 Master Agent 直接对用户暴露——表现为"可以自然语言查询任何 SSG GPS 领域知识"。这不是因为它是一个独立 Agent，而是因为没有操作类 Agent 时，所有查询都走 RAG → 用户。

到 Wave 2-4，当操作类 Agent 上线后，RAG 回归其共享管线角色，不再直接面向用户。

### 4.6 ISG Price Update Pipeline — 跨 Agent 协作示例

> **来源**：ISG Price Update 端到端 16 步流程。以下展示三个 Sub-Agent 如何串联完成一次完整的定价周期。

```
┌─────────────────────────────────────────────────────────────────┐
│                  ISG Price Update — Agent 协作流程                │
│                                                                   │
│  PN Agent                        Cost Agent        Price Agent   │
│  ────────                        ──────────        ───────────   │
│                                                                   │
│  ① Published PN Listing ─┐                                       │
│  ② Not-published PN    ─┤                                       │
│  ③ PN Master           ─┼─→ ④ Finalize PN List                  │
│  ④ HW-PN Compatibility ─┘       │                                │
│                                  ▼                                │
│                          ⑤ Pricing Dimensions Mapping ──────────→│
│                          ⑥ Charge Type 匹配 ─────────────────────→│
│                                                                   │
│  ⑦ EOS HW Listing ────────────→ ⑧ HW/EOS 数据接入               │
│                                  │                                │
│                                  ▼                                │
│                          ⑨ Channel Discount 管理                 │
│                          ⑩ Cost Pull (CFE)                        │
│                                  │                                │
│                                  ▼                                │
│                          ⑪ Brand Mapping → DP ───────────────────→│
│                          ⑫ List Price Pull (CPM) ────────────────→│
│                          ⑬ Forex Translation ────────────────────→│
│                                                                   │
│                                  │              ◄─────────────────│
│                                  ▼                                │
│                          ⑭ PN → CBSO 转换 ───────────────────────→│
│                          ⑮ Price Calc & Shaping ─────────────────→│
│                                  │              (综合所有输入)     │
│                                  ▼                                │
│                          ⑯ Upload to Tools                        │
│                             (审批 Gate → 自动写入 CPM/LBP)         │
└─────────────────────────────────────────────────────────────────┘
```

**协作模式**：
- **PN Agent** 负责上游（步骤 1-4,10）：确保进入定价的 PN 清单完整、去重、兼容性已验证
- **Cost Agent** 负责中游（步骤 6-7,9,12）：提供成本侧输入——HW 数据、渠道折扣、标准成本
- **Price Agent** 负责下游（步骤 5,8,11,13-15）：定价维度定义、价格拉取、汇率换算、最终价格计算
- **Security Layer**（贯穿全程）：步骤 10（锁定 PN 清单）、步骤 9（折扣更新）、步骤 15（价格发布）均走审批 Gate
- **RAG Knowledge Pipeline**（共享基础设施）：所有 Agent 共享 PN 规则、定价逻辑、审批矩阵

**关键依赖**：步骤 1-4 的 PN 清单质量直接决定后续定价的完整性——如果 Published PN 列表有遗漏，整个定价周期失效。因此 PN Agent 的「PN Listing & Finalize」是 ISG 流程的第一道质量门禁。

---

## 5. Security Layer 设计

### 5.1 操作分级

```
AUTO（Agent 自主执行）          APPROVAL（需人审批）
─────────────────────────      ─────────────────────────
• 数据查询（PN 信息检索）       • 标准成本写入 SCFE
• 重复检查                      • Sales Cost 写入 CPM
• 报告生成                      • List/Channel Price 发布
• PFV 竞品研究（只读）          • PN 批量关闭操作
• Booking Impact 分析           • Sub-Tier 定义确认
• 审批请求发送                  • 新 PN Portfolio 创建
• MT Announcement 捕获入库      • Brand Mapping 更新
• 异常/风险提醒                 • Channel Discount 数值写入
• Pricing Dimensions 模板定义   • PN 清单锁定（Finalize）
• HW/EOS 数据拉取（只读）
• Charge Type 自动匹配
• Forex 汇率换算
• PN → CBSO 自动转换
• List Price / Cost Pull（只读）
```

### 5.2 审批流

```
Agent 生成建议
  → 推送到 Persona Workspace 审批队列
  → 通知相关人员（Teams / 邮件）
  → 人审核 → 批准 / 拒绝 / 修改
  → 批准后 Agent 自动执行
  → 全链路 Audit Log
```

### 5.3 SaaS LLM 数据策略

- 传给 LLM 的数据做最小化处理（只传必要字段，不传完整数据集）
- Booking 数据做聚合/脱敏后再进 LLM 上下文
- 不在 LLM 对话中传输原始客户名称（用 ID 替代）

---

## 6. Channel 设计（全渠道，后端统一）

```
                    ┌─────────────────────┐
                    │   Unified Gateway   │
                    │   (DeerFlow IM      │
                    │    Gateway)          │
                    └──────────┬──────────┘
           ┌───────────────────┼───────────────────┐
           │                   │                   │
    ┌──────┴──────┐    ┌──────┴──────┐    ┌──────┴──────┐
    │ Teams Bot   │    │ Web App     │    │ Embedded    │
    └─────────────┘    └─────────────┘    └─────────────┘
    适合：              适合：              适合：
    • 快速查询          • 复杂操作          • 系统内操作
    • 审批通知          • 数据面板          • 流程中求助
    • "PN xxxx 的      • Persona          • 在 SPEP 里填
      sales cost？"     Workspace 全貌     表时问 Agent
```

---

## 7. Vetra 核心组件 — Agent 的能力底座

四个组件协同工作，使 Agent 不只是"带规则手册的聊天机器人"。

| 组件 | 做什么 | 在 PN 管理中的例子 |
|------|--------|------------------|
| **Memory** | 跨会话记忆：短期对话上下文、长期用户偏好、领域知识库 | "PN-88421 的成本？"→"渠道价呢？"——知道还在问同一个 PN。Sarah 的模板偏好被记住，第三次自动套用。底层对接 EKP + BCPF (Signavio) |
| **Skills** | 可复用能力封装，独立版本化、独立测试、可插拔 | PN Creation Skill 负责查重、POR 表单生成、SPEP 提交。升级它不影响 Cost Calculation 或 Pricing Skill |
| **Constraints** | 规则、权限、边界——确保 Agent 在受控范围内行动 | PN 创建需要 Manager 审批后才能提交 SPEP。定价偏离 >15% 触发强制复核。低置信推荐路由到人工 |
| **Sandbox** | 隔离执行环境，Agent 先在此验证再接触真实系统 | 生成新 PN 草稿时，Agent 在 Sandbox 中构建并校验，全部检查通过后才推到 SPEP |

**协作逻辑**：Memory 提供上下文 → Skills 执行任务 → Constraints 强制边界 → Sandbox 确保安全。四组件全部来源于 **Lenovo Skill Hub** 企业级平台。

---

## 8. 落地路径建议

```
Wave 1（MVP — 4-6 周）
├── RAG Knowledge Pipeline（场景 #1, #4, #12） ← 只读查询 + 知识检索
├── 知识库优先摄入 Pricing 领域（PFV 规则、Cost 计算逻辑、GP Floor 规则）
├── Teams Bot 上线（Master Agent 直接对用户暴露 RAG）
└── 验证"AI 辅助查询"的实际价值

Wave 2（定价核心 — 6-8 周）
├── Price Agent（ISG Price Update 7 步：步骤 5,8,11,13,14,15 + PFV 分析）
├── Cost Agent 扩展（Channel Discount + HW/EOS 数据接入）
├── Web Persona Workspace 上线（Pricing Workspace 优先）
└── 目标：从 PN 清单到最终售价的全链路自动化（ISG 16 步定价闭环）

Wave 3（成本计算 — 6-8 周）
├── Cost Agent（场景 #8, #9）
└── 标准成本计算 + Sales Cost Uplift → 定价全链路闭环

Wave 4（PN 保底 — 6-8 周）
├── PN Agent（场景 #2, #3, #7）
├── Lifecycle Agent（场景 #5）
└── 与已有 AI 实施互补，而非替代
    ├── PN 团队当前已在使用 AI 工具进行部分自动化
    ├── Spark / Copilot / Web Coding 等工具已覆盖重复性编码和表单生成场景
    └── 本阶段不重复建设已有能力，聚焦团队尚未覆盖的决策辅助与生命周期管理

Wave 5（持续优化）
├── Onboarding Agent（场景 #13）
├── 审批数据驱动优化
└── 跨角色协作优化
```

---

## 9. 与 iChain 架构对齐对照

| iChain 设计原则 | SSG Sales Enablement 对应 |
|----------------|--------------------------|
| Persona Workspace | GPS PM / Sales Enablement / Pricing / Finance 四个 Workspace |
| Persona Agent | 4 个 Sub-Agent (Price / Cost / PN / Lifecycle) + 共享 RAG Knowledge Pipeline |
| Human-in-the-loop | 半自动模式：成本/价格操作需审批 |
| Insight → Decision → Action | 分析 → 建议 → 审批 → 执行闭环 |
| Explainable AI | 定价建议附带 PFV 分析依据和计算逻辑 |
| Machine Suggestion | Agent 出建议，人做决策 |
| All Knowledge On-line | PN 主数据 + PFV + 流程规则 全部入 RAG 知识库 |
| Phase 1→2→3 演进 | Wave 1(查询)→2(Price)→3(Cost)→4(PN)→5(优化) |

---

## 10. 关键成功因素

1. **系统 API 可用性**：ICP/SPEP/SCFE/CPM/ODT/Concord 是否提供可被 Agent 调用的 API？
2. **审批流打通**：现有审批系统能否接收 Agent 发起的审批请求？
3. **知识库质量**：PN 流程、Service Tier 规则、审批规则是否有成文文档可供 RAG 摄入？
4. **数据新鲜度**：Booking 数据、MT Announcement 的实时性如何保证？

---

## 11. 持续改进闭环（Eval-driven Loop）

借鉴 Vetra 平台的 Eval-driven Loop 策略，SSG Agent 架构内建持续改进机制：

```
┌──────────────────────────────────────────────────────┐
│                 Eval-driven Loop                      │
│                                                       │
│  追踪 → 分析 → 优化 → 验证 → 追踪 → ...              │
│                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │ Quality  │  │ Latency  │  │ Cost     │            │
│  │ 质量指标  │  │ 延迟指标  │  │ 成本指标  │            │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘            │
│       │             │             │                   │
│       ▼             ▼             ▼                   │
│  审批通过率     端到端响应时间   Token/调用成本        │
│  建议采纳率     Sub-Agent耗时    API 调用次数         │
│  知识检索准确率  人工等待占比    模型费用趋势          │
└──────────────────────────────────────────────────────┘
```

**三类追踪指标**：

| 维度 | 指标 | 用途 |
|------|------|------|
| **Quality** | 审批通过率、建议采纳率、知识检索准确率 | 判断 Agent 输出是否可信、是否需要调整 prompt 或知识库 |
| **Latency** | 端到端响应时间、各 Sub-Agent 耗时、人工等待占比 | 定位性能瓶颈，优化 Sub-Agent 调度策略 |
| **Cost** | Token 消耗、模型调用成本、API 调用次数 | 控制运营成本，识别可优化为本地缓存的重复调用 |

**改进节奏**：每个 Wave 结束后收集 2-4 周数据 → 分析趋势 → 确定下个 Wave 的优化优先级 → 实施 → 验证。

---

## 12. 平台边界原则

SSG Sales Enablement Agent 运行在 Vetra 平台上，遵循明确边界：

> **Vetra 不替代现有系统——它编排、集成和可视化现有系统的能力。**

| Vetra 负责（编排层） | 业务系统保留（执行层） |
|---------------------|----------------------|
| Agent 工作流编排与调度 | SPEP：PN 创建/生命周期管理 |
| 跨系统 API 集成与数据聚合 | CPM：Sales Cost / Pricing 计算 |
| 结果可视化与状态追踪 | SCFE：标准成本数据 |
| 质量信号汇总与风险预警 | ODT：属性定义与变更 |
| 审批路由与 Audit Log | Concord / ICP：Booking 与公告 |
| Knowledge Pipeline（RAG + PageIndex） | 各系统的数据库和业务逻辑 |

**价值**：低侵入性集成——不改现有系统代码，不重建业务流程，只在上层增加 AI 编排能力。业务团队可以继续使用熟悉的系统，Agent 在后端自动串联数据流。
