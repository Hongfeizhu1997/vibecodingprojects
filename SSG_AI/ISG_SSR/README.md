# ISG SSR — 智能服务推荐方案探索

> SSG AI 子项目 #1 | 联想 ISG (Infrastructure Solutions Group) Service Smart Recommendation
> 侧重：方案探索 · 知识积累 · 文档生成

---

## 与 ServiceSmartRecommendationAnalysis 的关系

| 维度 | ServiceSmartRecommendationAnalysis | ISG SSR（本项目） |
|------|-----------------------------------|-------------------|
| 视角 | 事后分析 | 前瞻探索 |
| 内容 | 业务效果 KPI（Phase 1-3） | 方案设计、知识沉淀、文档产出 |
| 输出 | HTML/PDF 分析报告 | 方案书、白皮书、PPT、信息图 |
| 状态 | ✅ 已完成 | 🔄 进行中 |

---

## 项目结构

```
ISG_SSR/
├── README.md
├── analysis/
│   ├── models/
│   │   └── recommendation_model_overview.md   ← 模型技术参考（唯一权威）
│   └── insights/
│       ├── llm_explanation_generation.md       ← Stage 7 完整方案（含 Prompt + 示例）
│       ├── api_schema_model_catalog_contract.md ← API JSON Schema
│       ├── feature_business_language_mapping.md ← 特征映射表
│       └── model_explainability.md             ← 面向业务的可解释性说明
├── outputs/
│   ├── diagrams/       # 架构图/动画（7 个 HTML）
│   └── infographic/    # 信息图
├── notes/
│   └── progress.md     # 统一进度日志
└── references/         # 参考资料
```

---

## 已完成（截至 6/17）

### 核心方案文档（4 份 insights + 1 份 model）

| 文件 | 内容 |
|------|------|
| `analysis/insights/llm_explanation_generation.md` | **Stage 7 完整方案**：Prompt 模板（4 套）、Vetraflow+ChatGPT 集成、延迟分析、缓存、校验、降级、Few-shot 示例、端到端附录 |
| `analysis/insights/api_schema_model_catalog_contract.md` | **Model → Catalog JSON Schema**：完整字段定义 + 示例 + 概率约束 |
| `analysis/insights/feature_business_language_mapping.md` | **特征映射表**：30+ 特征 Internal/Customer 双版表述 |
| `analysis/insights/model_explainability.md` | **可解释性说明**：4 层推荐逻辑 + 信息图速查摘要 |
| `analysis/models/recommendation_model_overview.md` | **模型技术参考**：5 阶段 Pipeline、9 项确认、数学公式 |

### 可视化交付物

| 文件 | 说明 |
|------|------|
| `outputs/diagrams/isg-ssr-full-story.html` | **全故事总集（17 stage）** = A + B + C |
| `outputs/diagrams/part-a_model-explainer.html` | A：模型解释（Title→Context→Decision→Why→How） |
| `outputs/diagrams/part-b_workflow-animated.html` | B：核心工作流 + LLM Explanation |
| `outputs/diagrams/part-c_catalog-logic.html` | C：Catalog 消费逻辑 |
| `outputs/diagrams/isg-ssr-business-overview.html` | 业务总览（6 层架构） |
| `outputs/diagrams/isg-ssr-technical-architecture.html` | 技术架构（6 层架构） |
| `outputs/infographic/isg-ssr-explainability-infographic.html` | 可解释性信息图 |

---

## 5 项已确认关键决策（2026-06-17）

| # | 决策 | 结论 |
|---|------|------|
| 1 | 特征映射表 | 待定，不影响 high-level 方案 |
| 2 | LLM 提供商 | **Vetraflow + ChatGPT**（联想认可架构） |
| 3 | 生成时机 | 先按实时生成设计，最终视 performance 调整 |
| 4 | 多语言 | **需要**，含中文 Customer 版 |
| 5 | SHAP 特征 | 数量待定（Base ~8-10, Add-on ~3-5），值已离散化，含 Add-on |

---

## 下一步

| 优先级 | 事项 |
|--------|------|
| 1 | API Schema 评审确认 |
| 2 | Vetraflow 接入权限确认 |
| 3 | 4 套 Prompt 定稿 |
| 4 | 单条真实样本跑通 |
| 5 | Catalog 消费逻辑用户审查 |
