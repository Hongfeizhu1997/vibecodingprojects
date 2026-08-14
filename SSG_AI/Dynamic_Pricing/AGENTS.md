# AGENTS.md — Dynamic Pricing

> 自动加载于 agent 进入本项目时。全局规则见 Hermes 记忆。

## 项目定位

SSG 服务交易价格动态优化。面向 GPS 服务 PN 的最终交易售价（Sales Price），模型选型 + 竞品调研 + 方案设计。

与 Sales Enablement Agent 的分工：Sales Enablement = 主数据层（List Price），Dynamic Pricing = 交易层（Sales Price）。

## 关键路径

| 内容 | 路径 |
|------|------|
| 决策记录 | `DECISIONS.md` |
| 方案产出 | `outputs/diagrams/` |
| 分析笔记 | `analysis/` |

## 领域知识（Wiki）

| 主题 | 链接 |
|------|------|
| DP 模型总览（ISG=PenRate, IDG=Band+Term+αγ） | `/root/wiki/business/dynamic-pricing-models.md` |
| ISG B2B Pen Rate（~5%, Floor 规则） | `/root/wiki/business/isg-b2b-penrate.md` |
| SSG BM Matrix | `/root/wiki/business/ssg-business-model-matrix.md` |

## HTML 产出规则

- 全英文（`[RULE]`）
- 设计规范 → `html-infographic-legibility.md` skill
- 生成前先确认 Light/Dark 主题
