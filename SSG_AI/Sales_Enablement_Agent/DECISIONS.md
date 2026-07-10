# Decisions — Sales Enablement Agent

> SSG AI 子项目 #2 持久化决策记录。只增不改。

---

## 2026-05 — 设计理念：iChain Persona Workspace 模式

- **Status**: Active
- **Context**: Agent 的架构模式选择——通用 Chatbot 还是角色化 Persona？
- **Decision**: 借鉴 iChain Persona Workspace & Agent 框架，每个业务角色（GPS PM / TMO / SMO / Finance）对应一个 Persona Agent，而非单一通用 Agent。
- **Consequence**:
  - 每个 Persona 有独立的上下文、权限和技能集
  - iChain 适配清单已完成（analysis/insights/ichain_adaptation_checklist.md）
  - 技术底座复用 DeerFlow (Vetraflow) + Lenovo Hybrid AI Platform

---

## 2026-05 — 技术底座选型：DeerFlow (Vetraflow)

- **Status**: Active
- **Context**: 自建 Agent 编排 vs 使用联想内部平台？
- **Decision**: 使用 DeerFlow（后改名 Vetraflow）作为 Agent 编排引擎。平台评估已完成（analysis/insights/platform_evaluation.md）。
- **Consequence**:
  - 复用联想现有的模型、知识库、数据基础设施
  - 不与 ISG SSR 的自有模型共享底层，但在 Vetra 层可互操作
  - Agent 开发聚焦业务逻辑，不重复造编排轮子

---

## 2026-06 — 架构 V1：三阶段递进

- **Status**: Active
- **Context**: 13 个 AI 场景不可能一次性交付，需要分阶段。
- **Decision**: 架构 V1（analysis/insights/architecture_v1.md）定义三阶段：
  1. **Knowledge Pipeline** — 信息捕获和知识沉淀（场景 4、10）
  2. **Teams Bot** — 主数据查询和操作辅助（场景 7、9、11、12）
  3. **Full Agent** — 完整的 Persona Agent 协作（场景 1、2、3、5、6、8、13）
- **Consequence**:
  - Wave 1 MVP 聚焦 Knowledge Pipeline + Teams Bot
  - 最核心的 PN 操作自动化（场景 7、9、11）在 Phase 2
  - 不追求一次交付所有场景

---

## 2026-06 — 知识库方案：Hybrid RAG + 结构化索引

- **Status**: Active
- **Context**: Sales Enablement Agent 需要回答"这个 PN 的定价规则是什么"、"ODT 变更影响哪些 Booking"等知识密集型问题。
- **Decision**: 采用 Hybrid RAG + PageIndex（结构化可追踪），与母项目一致。知识来源：ICP 系统数据、SPEP 规则、Concord 流程文档。
- **Consequence**:
  - 每条知识可追溯到源系统
  - 知识更新不影响其他查询
  - 为 Teams Bot 的知识问答场景提供基础

---

## 2026-06 — 与 Dynamic Pricing 的边界

- **Status**: Active
- **Context**: 两个子项目都涉及"定价"，需分工明确。
- **Decision**: Sales Enablement Agent 管**主数据层**——List Price / Channel Price 的定期发布和人工审批辅助。Dynamic Pricing 管**交易层**——每笔交易的 Sales Price 模型驱动优化。
- **Consequence**:
  - SEA 输出的 List Price 作为 DP 的输入
  - SEA 不做 AI 驱动定价，DP 不做 PN 创建
  - 两项目共享服务 PN 主数据但互不侵入业务逻辑
