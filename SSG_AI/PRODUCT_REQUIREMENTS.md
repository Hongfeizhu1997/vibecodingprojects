# Product Requirements — SSG AI

> SSG 传统业务 × AI 咨询项目母舰

---

## Product Goal

面向联想 SSG（Solutions & Services Group），系统化探索 AI 在传统服务业务中的应用，产出可交付的方案设计、技术架构和落地路径。

**不是 coding 项目，是咨询类项目**——输出方案书、白皮书、架构图、PPT、信息图等咨询交付物。

## Target Users

- 主要消费方：SSG 业务团队、产品经理、技术决策者
- 业务场景：服务产品定价、销售赋能、智能推荐等
- 成功标准：方案可落地、可被业务团队直接评审和使用

## Product Principles

- 方案自信自洽，不依赖外部团队成功案例背书
- 设计借鉴无声融入方案本身，不单独标注来源
- 不使用自造新概念/术语，用最简单的业务语言
- 解释"怎么做"而非仅陈述结论（如"X 作为 Y 的一个输入字段"而非"X 与 Y 不耦合"）

## Functional Requirements

### 子项目
1. **ISG SSR** — 智能服务推荐方案探索（ISG 线）
2. **Sales Enablement Agent** — AI 驱动的 SSG GPS 销售运营赋能
3. **Dynamic Pricing** — AI 驱动的服务交易价格动态优化

### 输出格式
- 方案书 / 白皮书（Markdown）
- 架构图（HTML/SVG 深色主题）
- 信息图
- PPT 演示
- 交互原型

## Architecture Requirements

- 技术底座：DeerFlow (Vetraflow) + Lenovo Hybrid AI Platform
- 知识库：Hybrid RAG + PageIndex（结构化可追踪）
- 各子项目独立演进，共享技术底座和统一设计语言

## Release Requirements

- HTML 产出：深色主题，≥0.62rem 字号，动画禁字符串替换
- 演示文档：骨架要点（≤1 行/条），卡片网格/标签/流程图，禁大段文字
