# SSG Sales Enablement Agent — 架构方案 V1

> 创建：2026-06-03 | 更新：2026-06-10 | 来源：iChain Persona Workspace + DeerFlow (Vetraflow) + SSG GPS 业务需求 + ITshare Engineering & AI Workshop (2026 May)

---

## 1. 设计理念

**一句话**：为 SSG GPS 每个角色构建 Persona Agent，覆盖服务 PN 从创建到退出的全生命周期。

借鉴 iChain 三层模型：`Persona Workspace → Persona Agent → Execution Loop`，技术底座用 DeerFlow (Vetraflow) + Lenovo Hybrid AI Platform。

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
│      │         │         │         │          │             │
│  ┌───┴──┐ ┌───┴──┐ ┌───┴──┐ ┌───┴───┐                     │
│  │PN    │ │Cost  │ │Price │ │Life-  │                     │
│  │Agent │ │Agent │ │Agent │ │cycle  │                     │
│  │      │ │      │ │      │ │Agent  │                     │
│  └──┬───┘ └──┬───┘ └──┬───┘ └──┬────┘                     │
│     │        │        │        │                           │
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
│  │  DeerFlow (Vetraflow)                              │   │
│  │  Sub-Agent · Sandbox · Memory · Skills · Gateway   │   │
│  └────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────┘
```

---

## 3. 角色与 Persona Agent 映射

| 角色 | 主要场景 | 对应 Sub-Agent | Workspace 焦点 |
|------|---------|---------------|---------------|
| **GPS PM** | PN 创建、生命周期管理 | PN Agent, Lifecycle Agent | PN 创建视图、审批队列 |
| **Sales Enablement** | Sales Cost 计算、验证、发布 | Cost Agent | Cost 数据面板、审批 |
| **Pricing Team** | PFV 分析、定价计算 | Price Agent（共享 Knowledge Pipeline） | 定价工作台、竞品对标 |
| **Finance Team** | 标准成本计算 | Cost Agent | 成本数据输入 |
| **TMO/SMO/SA** | PN 需求提交 | PN Agent（共享 Knowledge Pipeline） | 需求提交 + 流程指南 |
| **Offering Mgr / Portfolio Lead** | PN 报告查询 | Knowledge Pipeline（RAG 直接查询） | 客制化报告 |

---

## 4. Sub-Agent 能力矩阵

### 4.1 PN Agent（PN 全生命周期）
| 场景 | 能力 | 权限 |
|------|------|------|
| #2 自动生成 POR/表单 | 接收需求信息 → 调 SPEP API 生成 | **自动** |
| #3 重复检查 | PN 编号/属性 → 调 SPEP 查重 → 返回建议 | **自动** |
| #7 创建/扩展判断 | 分析 MT 归属 → 建议 extend 或 create new | **半自动**（涉及新 PN Portfolio 创建需审批） |

### 4.2 Cost Agent（成本管理）
| 场景 | 能力 | 权限 |
|------|------|------|
| #8 标准成本计算 | 从 SCFE 取 PH3 数据 → 加权平均计算 → 展示 | **审批后写入** |
| #9 Sales Cost Uplift | 分析历史 uplift 规则 → 建议规则和数值 | **审批后写入 CPM** |
| Sales Cost 验证 | 对标 HW AUR → 完整性检查 → 报告异常 | **自动**（只读） |

### 4.3 Price Agent（定价）
| 场景 | 能力 | 权限 |
|------|------|------|
| #6 Sub-Tier 定义 | 读 MT target price → 模型分析 sub-tier 归属 → 建议 | **审批后确认** |
| #10 PFV 分析 | 自动抓取行业/竞品价格 → 生成对标报告 | **自动**（只读研究） |
| #11 定价计算 | 输入 Std Cost + PFV → 计算 List/Channel Price → 建议 | **审批后发布** |

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
• MT Announcement 捕获入库
• 异常/风险提醒
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

## 7. Memory System

借鉴 DeerFlow + iChain 的 Memory 体系：

| 记忆类型 | 内容 | 生命周期 |
|---------|------|---------|
| **Short-term** | 当前对话上下文、正在操作的 PN、任务状态 | 单次会话 |
| **Long-term** | 用户偏好、常用 PN、历史决策偏好、角色习惯 | 跨会话持久化 |
| **Domain** | PN Lifecycle 规则、审批规则、定价逻辑、Service Tier 体系 | 团队共享知识库 |

---

## 8. 落地路径建议

```
Wave 1（MVP — 4-6 周）
├── RAG Knowledge Pipeline（场景 #1, #4, #12） ← 只读查询 + 知识检索
├── Teams Bot 上线（Master Agent 直接对用户暴露 RAG）
└── 验证"AI 辅助查询"的实际价值

Wave 2（操作自动化 — 6-8 周）
├── PN Agent（场景 #2, #3, #7）
├── Lifecycle Agent（场景 #5）
├── Web Persona Workspace 上线
└── 验证"半自动 PN 管理"

Wave 3（定价与成本 — 8-10 周）
├── Cost Agent（场景 #8, #9）
├── Price Agent（场景 #6, #10, #11）
├── 系统嵌入式 Widget
└── 完整定价闭环

Wave 4（持续优化）
├── Onboarding Agent（场景 #13）
├── 审批数据驱动优化
└── 跨角色协作优化
```

---

## 9. 与 iChain 架构对齐对照

| iChain 设计原则 | SSG Sales Enablement 对应 |
|----------------|--------------------------|
| Persona Workspace | GPS PM / Sales Enablement / Pricing / Finance 四个 Workspace |
| Persona Agent | 4 个 Sub-Agent (PN / Cost / Price / Lifecycle) + 共享 RAG Knowledge Pipeline |
| Human-in-the-loop | 半自动模式：成本/价格操作需审批 |
| Insight → Decision → Action | 分析 → 建议 → 审批 → 执行闭环 |
| Explainable AI | 定价建议附带 PFV 分析依据和计算逻辑 |
| Machine Suggestion | Agent 出建议，人做决策 |
| All Knowledge On-line | PN 主数据 + PFV + 流程规则 全部入 RAG 知识库 |
| Phase 1→2→3 演进 | Wave 1(查询)→2(操作)→3(定价)→4(优化) |

---

## 10. 关键成功因素

1. **系统 API 可用性**：ICP/SPEP/SCFE/CPM/ODT/Concord 是否提供可被 Agent 调用的 API？
2. **审批流打通**：现有审批系统能否接收 Agent 发起的审批请求？
3. **知识库质量**：PN 流程、Service Tier 规则、审批规则是否有成文文档可供 RAG 摄入？
4. **数据新鲜度**：Booking 数据、MT Announcement 的实时性如何保证？
