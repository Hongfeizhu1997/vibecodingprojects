# AGENTS.md — ISG SSR

> 自动加载于 agent 进入本项目时。全局规则见 Hermes 记忆。

## 项目定位

ISG 智能服务推荐方案探索。前瞻分析 + 文档产出，与 ServiceSmartRecommendationAnalysis 的事后 KPI 分析互补。

## 关键路径

| 内容 | 路径 |
|------|------|
| 模型技术参考 | `analysis/models/recommendation_model_overview.md` |
| Stage 7 LLM 解释方案 | `analysis/insights/llm_explanation_generation.md` |
| 验证输出 | `validation_output/` |
| 决策记录 | `DECISIONS.md` |

## 领域知识（Wiki）

| 主题 | 链接 |
|------|------|
| DP 模型（ISG=PenRate, IDG=Band+Term+αγ） | `/root/wiki/business/dynamic-pricing-models.md` |
| ISG B2B Pen Rate（~5%, Floor 规则） | `/root/wiki/business/isg-b2b-penrate.md` |
| SSR 产品定义（WT+Term+SLA 三位一体；SLA 仅 Four Hours / NBD 两种） | `/root/wiki/business/isg-ssr-product-definition.md` |
| SSG BM Matrix | `/root/wiki/business/ssg-business-model-matrix.md` |

## HTML 产出规则

- 全英文（`[RULE]`）
- 设计规范 → `html-infographic-legibility.md` skill
- 生成前先确认 Light/Dark 主题
- 翻页动画：每页自洽，不跨页对齐
- Split-row：`stretch` + `space-between` + 压缩图表高度
