# Decisions — ISG SSR

> SSG AI 子项目 #1 持久化决策记录。只增不改。

---

## 2026-05 — 项目定位：前瞻探索 vs 事后分析

- **Status**: Active
- **Context**: ServiceSmartRecommendationAnalysis 已完成事后分析（KPI Phase 1-3），ISG SSR 要做什么？
- **Decision**: ISG SSR 定位为**前瞻探索**——方案设计、知识沉淀、文档产出。与 ServiceSmartRecommendationAnalysis 的事后分析形成互补而非重复。
- **Consequence**:
  - 不重复做 KPI 计算
  - 输出以方案书/白皮书/架构图为主
  - ServiceSmartRecommendationAnalysis 的 KPI 结论作为输入参考

---

## 2026-05 — 推荐模型：5 阶段 + LLM 解释

- **Status**: Active
- **Context**: 智能服务推荐需要怎样的模型架构？
- **Decision**: 5 阶段 Pipeline + Stage 7 LLM Explanation Generation。模型技术参考见 analysis/models/recommendation_model_overview.md（唯一权威）。
- **Consequence**:
  - Pipeline 各阶段可独立测试和优化
  - LLM 解释层是可替换的（不绑定单一模型）
  - 4 套 Prompt 模板覆盖不同推荐场景

---

## 2026-06-17 — 5 项已确认关键决策

- **Status**: Active
- **Context**: 2026-06-17 方案评审中确认的 5 项关键决策。

### #1 特征映射表 — 待定
- **Decision**: 特征映射表不影响 high-level 方案，暂不细化。
- **Consequence**: 后续在实施阶段补充。

### #2 LLM 提供商 — Vetraflow + ChatGPT
- **Decision**: 使用 Vetraflow + ChatGPT（联想认可架构），不做自建 LLM 网关。
- **Consequence**: 复用联想现有的模型调用链路和安全合规。

### #3 生成时机 — 先按实时设计
- **Decision**: 推荐解释先按实时生成设计，最终视性能测试结果调整为预生成/缓存。
- **Consequence**: Stage 7 方案含延迟分析和缓存设计作为 fallback。

### #4 多语言 — 需要
- **Decision**: 需要多语言支持，含中文 Customer 版表述。
- **Consequence**: 特征映射表需维护 Internal/Customer 双版；4 套 Prompt 需多语言适配。

### #5 SHAP 特征 — Base ~8-10 + Add-on ~3-5
- **Decision**: SHAP 特征数量：Base 8-10 个 + Add-on 3-5 个。值已离散化，含 Add-on。
- **Consequence**: 模型可解释性输出聚焦这 10-15 个特征。

---

## 2026-05~06 — KPI 分析方法论：三阶段演进

- **Status**: Active
- **Context**: KPI 分析需要方法论框架，但分析方法本身有分歧。
- **Decision**: 三阶段演进路径：
  - **Phase 1**: 操作 KPI（Coverage / Acceptance / Attach Rate）
  - **Phase 2 V1**: 财务 KPI — DiD + 收入分解法（$13.6M 归因）
  - **Phase 2 V2**: 财务 KPI — 恒定服务价格框架（$28.3M，假设服务产品价格不随时间变化）
  - **Phase 3**: 整合验证 — 操作 KPI ↔ 财务 KPI 交叉验证（V1 用 DiD 框架，V2 用恒定价格框架）
- **Consequence**:
  - V1 和 V2 是两个并列的分析框架，各有利弊
  - 整合验证阶段不选边，两套框架都跑交叉验证
  - 业务方可根据场景选择合适的归因逻辑
