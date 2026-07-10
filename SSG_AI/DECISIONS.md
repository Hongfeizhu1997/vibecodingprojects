# Decisions — SSG AI

> SSG AI 咨询项目母舰级持久化决策记录。只增不改。

---

## 2026-04 — 项目定位：咨询类而非 Coding 项目

- **Status**: Active
- **Context**: SSG AI 项目到底做产品还是做咨询？早期方向不明。
- **Decision**: 定位为**咨询类项目**——输出方案书、白皮书、架构图、PPT，而非可部署的软件产品。子项目各自侧重方案探索。
- **Consequence**:
  - 项目不追求代码可部署性
  - 交付物以文档/图表为主
  - 各子项目输出物独立评估

---

## 2026-05 — 技术底座：DeerFlow (Vetraflow) + Lenovo Hybrid AI Platform

- **Status**: Active
- **Context**: ISG SSR 和 Sales Enablement Agent 都需要 Agent 编排底座。自建 or 复用？
- **Decision**: 使用联想内部 DeerFlow（后改名 Vetraflow）作为 Agent 编排引擎，复用 Lenovo Hybrid AI Platform 的基础设施（模型、知识库、数据、工具）。
- **Consequence**:
  - ISG SSR 复用 Vetraflow + ChatGPT 方案
  - Sales Enablement Agent 基于 DeerFlow 设计 Persona Agent
  - Dynamic Pricing 模型层独立，但复用 Vetraflow 接口

---

## 2026-05 — Vetra 2.0 四核心架构

- **Status**: Active
- **Context**: Vetra 从 1.0 升级到 2.0，需要明确核心能力边界。
- **Decision**: Vetra 2.0 定义四核心：**Memory**（跨会话状态/知识连续性）、**Skills**（可复用能力封装）、**Constraints**（规则/权限/边界）、**Sandbox**（隔离执行环境）。
- **Consequence**:
  - 所有子项目的 Agent 设计必须对齐这四层
  - Vetra 不替代 GitLab / Jira / Confluence / 测试平台，只做编排/集成/可视化

---

## 2026-05 — 知识库策略：Hybrid RAG + PageIndex

- **Status**: Active
- **Context**: 各子项目需要访问业务知识（服务 PN 属性、定价规则、推荐逻辑等）。
- **Decision**: 采用 Hybrid RAG（检索增强生成）+ PageIndex（结构化可追踪索引），而非纯向量检索。
- **Consequence**:
  - 每一段知识有明确的来源页面可追踪
  - 知识更新不影响整体索引结构
  - 为 ISG SSR 的推荐解释和 Sales Enablement 的知识问答提供基础

---

## 2026-06 — 开发策略：四阶段递进

- **Status**: Active
- **Context**: 多个子项目并行，需要统一的开发节奏。
- **Decision**: **Workflow-First → Skill-as-Product → Agent Assembly → Eval-driven Loop**。先定义业务工作流，再封装为可复用 Skill，再组装为 Agent，最后用评估数据迭代。
- **Consequence**:
  - 每个子项目不跳过 Workflow 定义阶段
  - Skill 封装后才能进入 Agent 组装
  - IDG CS SW Agent Phase 1（6-8月）正在此框架下进行

---

## 2026-06 — 方案呈现风格约定

- **Status**: Active
- **Context**: 咨询方案需要专业呈现，避免 AI 腔和防御性论证。
- **Decision**:
  - 不引用内部其他团队的成功来证明自己方案的正确性（显得防御/派生）
  - 设计借鉴应无声融入方案本身，不单独标注来源页
  - 方案应自信、自洽，不依赖外部验证背书
  - 演示文档：骨架要点用卡片网格/标签/流程图，禁大段文字
- **Consequence**:
  - 所有子项目的交付物遵循此风格
  - 评审时以此为标准检查

---

## 2026-06 — HTML 设计语言：深色主题统一规范

- **Status**: Active
- **Context**: ISG SSR 和 Dynamic Pricing 产出大量 HTML 可视化，需统一视觉。
- **Decision**: 深色主题，最小字号 ≥0.62rem，需验证对比度。动画实现禁止字符串替换方式。标题标注 `[static]` 或 `[animated]`。
- **Consequence**:
  - 与 GPS Workbench 的浅色设计语言独立
  - 新 HTML 产出需对比度验证
  - 动画合并遵循既定流程

---

## 2026-07 — 项目治理：引入 DECISIONS.md

- **Status**: Active
- **Context**: 已有的 Memory 系统捕获了部分决策但散落在各处，缺乏项目本地的可发现性。
- **Decision**: 引入 Vibe Enterprise PoC 风格的 DECISIONS.md，项目级持久化决策记录。所有决策（无论大小）先宽记录，后续每周 Review 调整颗粒度。
- **Consequence**:
  - SSG_AI 父级和每个子项目维护独立的 DECISIONS.md
  - 决策记录只增不改
  - 新项目启动时同时创建 DECISIONS.md 模板
