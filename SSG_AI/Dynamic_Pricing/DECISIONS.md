# Decisions — Dynamic Pricing

> SSG AI 子项目 #3 持久化决策记录。只增不改。

---

## 2026-05 — 核心公式：ServicePrice = HWPrice × PenRate

- **Status**: Active
- **Context**: 服务定价如何与硬件价值挂钩？需要一个清晰的基础公式。
- **Decision**: 服务价格 = 硬件价格 × PenRate（渗透率）。ISG（服务器）用固定查表的方式确定 PenRate，IDG（PC）用 AI 计算。
- **Consequence**:
  - 服务定价始终围绕硬件底盘展开
  - ISG 和 IDG 采用不同的 PenRate 确定方式
  - SSG 服务因硬件底盘不同使用不同方法论

---

## 2026-05 — ISG vs IDG 方法论分叉

- **Status**: Active
- **Context**: 服务器和 PC 的定价逻辑差异很大，能否用一套方法？
- **Decision**: 分叉处理。ISG 采用固定查表（服务器配置标准化程度高），IDG 采用 AI 计算（PC 型号和配置变化频繁）。
- **Consequence**:
  - 两条代码路径，不强行统一
  - 两条路径共享 Price Band 输出格式

---

## 2026-06 — V3 方案：6 步引擎 → Price Band (F/T/S) + Reason + Confidence

- **Status**: Active
- **Context**: V2 方案（贝叶斯+弹性模型）过于学术化，业务方难以理解和信任。
- **Decision**: V3 采用 6 步引擎流水线，输出三层 Price Band（Floor / Target / Stretch），每条推荐附带 Reason Code 和 Confidence Score。
- **Consequence**:
  - 业务方可直接看 Price Band 做决策，不需理解底层模型
  - Reason Code 提供可解释性（为什么推荐这个价格）
  - Confidence 提供风险提示
  - V2 归档至 analysis/insights/product-pricing-recommendation-v2.md

---

## 2026-06 — Wave 1 聚焦 B2B：LBPi + LBPe

- **Status**: Active
- **Context**: B2B 和 B2C 的定价逻辑差异大，一次性覆盖风险高。
- **Decision**: Wave 1 只覆盖 B2B 渠道——LBPi（Lenovo lead direct sale）+ LBPe（Partner lead indirect sale）。B2C 作为后续 Wave。
- **Consequence**:
  - 引擎框架设计为渠道无关（便于后续横向拓展）
  - 当前样本和验证都基于 B2B 数据
  - 价格发现使用 B2B 特定的 Comparable Benchmark

---

## 2026-06 — 与 Sales Enablement Agent 的分工边界

- **Status**: Active
- **Context**: Dynamic Pricing 和 Sales Enablement Agent 都涉及"定价"，需要明确分工。
- **Decision**: Sales Enablement Agent 负责主数据层（List Price / Channel Price——定期发布，人工审批+Agent 辅助），Dynamic Pricing 负责交易层（Sales Price = 基准价 − 折扣——每笔交易，模型驱动）。
- **Consequence**:
  - SEA 的输出（List Price / Channel Price）作为 DP 的主数据输入
  - DP 不做 PN 创建/生命周期管理
  - PAIDS SSG Pen Rate Pricing 作为 DP 的参考基线和潜在集成点

---

## 2026-06 — 关键术语统一

- **Status**: Active
- **Context**: 跨团队沟通需要统一术语，避免歧义。
- **Decision**: 统一使用以下术语：
  - **PFV** = Product Fair Value（产品市场参考价/竞品价）
  - **LBPi** = Lenovo lead direct sale（直销）
  - **LBPe** = Partner lead indirect sale（渠道）
  - **Price Band** = 三档推荐：Floor / Target / Stretch
  - **DOA** = Delegation of Authority（审批授权阈值）
  - **Comparable Benchmark** = 可比较基准（accept price range / pen rate / win-loss）
- **Consequence**:
  - 所有文档和讨论使用统一术语
  - 新加入者通过 README 术语表快速上手

---

## 2026-06 — 业务沟通：禁用自造术语

- **Status**: Active
- **Context**: AI 咨询方案容易引入自造概念，让业务方困惑。
- **Decision**: 禁止创造新概念/术语（如"传导衰减率"），用直白的业务语言说清楚目的（如"让服务价格跟着硬件价格走"）。展示场景用阶段卡片聚合而非长段落。
- **Consequence**:
  - V3 方案已按此原则重写
  - 评审时检查是否有自造术语
  - 未来方案沿用此标准
