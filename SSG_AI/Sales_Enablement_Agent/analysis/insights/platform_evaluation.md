# 平台方案评估 — Sales Enablement Agent

> 创建：2026-06-03 | 状态：初稿，多个假设待验证

---

## 核心需求回顾

- 面向 SSG 业务团队（非技术用户）
- 两大场景：**业务日常问答** + **运营操作（Operation）**
- 产出：咨询方案（架构设计 + 落地路径）

---

## 候选平台分析

### 1. Microsoft Copilot Studio

| 维度 | 评估 |
|------|------|
| 适用场景 | 简单 FAQ、知识问答、轻量工作流 |
| 集成能力 | M365 / Teams / Power Platform 天然打通 |
| 开发门槛 | 低代码，业务团队可自助维护知识库 |
| 定制深度 | 有限——复杂多步推理、自定义工具调用受限 |
| 部署模式 | SaaS，依赖 Azure OpenAI [待确认] |
| 数据安全 | Microsoft 企业级合规 [待确认 Lenovo 是否已有相关协议] |

**适合**：快速搭建 Q&A Bot，作为第一阶段快速验证。
**不适合**：复杂的 operation 场景（多系统联动、多步决策）。

### 2. LangChain 自建 Agent

| 维度 | 评估 |
|------|------|
| 适用场景 | 复杂多步推理、自定义工具链、深度集成 |
| 集成能力 | 任意内部 API / 数据库 / 系统 |
| 开发门槛 | 需要开发团队（Python），持续维护 |
| 定制深度 | 无限制——完全自主控制 |
| 部署模式 | 自建服务器或容器化部署 |
| 数据安全 | 取决于 LLM 后端选择（可本地部署开源模型，也可调 Azure OpenAI） |

**适合**：复杂 operation 自动化、深度系统集成。
**不适合**：快速上线、非技术团队直接维护。

### 3. DeerFlow（字节跳动开源）

| 维度 | 评估 |
|------|------|
| 全称 | Deep Exploration and Efficient Research Flow |
| 定位 | 开源 Super Agent Harness（编排层），不是单体 Agent |
| 语言 | Python 3.12+ / TypeScript |
| 许可 | MIT |
| Stars | 70K+（GitHub Trending #1, 2026-02-28） |
| 核心能力 | Sub-Agent 并行调度、Sandbox 隔离执行、Skills 可插拔技能、Long-Term Memory、Context Engineering |
| 部署模式 | Docker（推荐）/ 本地开发 |
| LLM 后端 | 模型无关，兼容 OpenAI API，推荐 DeepSeek v3.2 / Doubao-Seed-2.0 / Kimi 2.5 |
| 安全设计 | 默认仅监听 127.0.0.1，仅本地可信环境；Docker Sandbox 隔离 bash 执行 |

**关键架构特性：**

1. **Sub-Agent 编排**：复杂任务自动分解为多个子 Agent 并行执行，各自拥有独立上下文和工具集，主 Agent 聚合结果。支持「分钟到小时级」的长任务。

2. **Skills 系统**：技能以 Markdown 文件定义，按需加载（不占满上下文窗口）。内置技能包括：深度研究、报告生成、幻灯片创建、网页制作、图像/视频生成。支持通过 `.skill` 包扩展自定义技能。

3. **Sandbox 执行环境**：每个任务有独立文件系统（uploads / workspace / outputs）。支持容器隔离执行 bash 命令，真正做到「不只是聊天，而是干活」。

4. **Long-Term Memory**：跨会话持久化——用户画像、偏好、知识积累。本地存储，用户完全掌控。

5. **Context Engineering**：子 Agent 上下文隔离 + 自动摘要压缩 + 工具调用恢复机制。

6. **可嵌入 Python Client**：无需起 HTTP 服务，直接在 Python 进程中调用。

7. **IM 频道集成**：支持消息网关，对接 IM 平台。

**适合**：复杂的多步骤 operation（研究+分析+产出）、需要 Sub-Agent 并行拆解的场景、需要持久记忆的长期使用场景。
**不适合**：简单 FAQ Bot（杀鸡用牛刀）、需要非技术人员直接维护的场景。

> 来源：https://github.com/bytedance/deer-flow | 调查时间：2026-06-03

---

## 三平台对比总结

| 维度 | Copilot Studio | LangChain 自建 | DeerFlow |
|------|---------------|---------------|----------|
| 开发速度 | ⭐⭐⭐ 最快 | ⭐ 慢 | ⭐⭐ 中等 |
| 定制深度 | ⭐ 受限 | ⭐⭐⭐ 无限制 | ⭐⭐⭐ 高（Skills + Sub-Agent） |
| 多步操作 | ⭐ 弱 | ⭐⭐ 需手写编排 | ⭐⭐⭐ 内置 Sub-Agent 拆解 |
| 记忆持久化 | ⭐ 弱 | ⭐⭐ 需自建 | ⭐⭐⭐ 内置 Long-Term Memory |
| 安全隔离 | SaaS 自带 | 需自建 | Docker Sandbox 内置 |
| 维护成本 | ⭐⭐⭐ 低（SaaS） | ⭐ 高（全自建） | ⭐⭐ 中（开源，需运维） |
| 非技术用户友好 | ⭐⭐⭐ Teams 直接用 | ⭐ 需开发界面 | ⭐⭐ 有 IM Gateway |

## 基础设施层确认：Lenovo Hybrid AI Platform

从 iChain Persona Workspace 文档确认，联想内部有 **Lenovo Hybrid AI Platform** 作为统一的 AI 基础设施层，承载：

```
Lenovo Hybrid AI Platform
├── Models（模型）
├── Knowledge（知识库）
├── Data（数据）
└── Tools（工具/API）
```

这意味着 Sales Enablement Agent 可以复用这一层，不需要从零建设。

## iChain 设计理念参考

iChain（供应链 Persona Workspace & Agent）的设计理念可直接指导 Sales Enablement Agent 的方案设计。详见 `analysis/insights/ichain_adaptation_checklist.md`。

**关键对齐**：
- **DeerFlow (Vetraflow)** = 技术底座（Agent 编排、Sandbox、Memory、Skills）
- **iChain 理念** = 上层设计模式（Persona Workspace、Human-Agent Team、闭环执行）
- **Lenovo Hybrid AI Platform** = 基础设施（模型、知识、数据、工具）

基于 DeerFlow 的实际能力，**推荐方案**从「Copilot + LangChain 混合」调整为：

```
核心引擎：DeerFlow
  ├── Sub-Agent 编排：复杂 operation 自动拆解
  ├── Skills 扩展：SSG 专属技能（查客户、查订单、生成报表等）
  ├── Long-Term Memory：销售团队成员偏好和常用操作
  ├── Sandbox：安全执行操作，隔离内部系统调用
  └── IM Gateway：对接 Teams 等终端

前端渠道：Copilot Studio（可选）
  └── 简单 FAQ / 知识检索类问题，直接 Teams 内快速响应
```

**理由**：
- DeerFlow 的 Sub-Agent + Skills 架构天然匹配「问答 + Operation」双需求
- 内置 Memory 解决「记住每个销售的偏好」问题
- Sandbox 隔离比手写 LangChain 安全
- MIT 开源，无供应商锁定
- 推荐 LLM 中包含 DeepSeek，与用户偏好一致

---

## 待确认清单

1. [x] DeerFlow 能查清——已确认是字节开源 Super Agent Harness（70K+ stars, MIT）
2. [ ] 需要对接哪些内部系统（CRM / ERP / 工单 / SharePoint /其他）？
3. [ ] 用户通过什么渠道使用（Teams / Web / 独立应用）？
4. [ ] 数据安全限制——能否用 Azure OpenAI？还是必须本地部署 LLM？
5. [x] ~~DeerFlow + Skill Hub 的具体能力~~ → 字节开源 DeerFlow，已调查完毕
6. [ ] 是否有内部 AI 平台团队可提供支持？

## 新发现：Vetra = 联想公司级 Agent 编排平台

从 `references/Vetraflow wukong.pptx` + NextOra SW Dev Agent Phase1 方案（2026.6）确认：

- **Vetra（VetraFlow）** 是联想公司级 Agent 编排平台，基于 DeerFlow（process-driven multi-agent orchestration）构建
- **DeerFlow** 是底层开源框架（字节跳动，MIT），**Vetra** 是联想内部部署实例名——关系类似 Kubernetes 是框架、某个内部 K8s 集群是平台
- Vetra 2.0 四大核心组件：**Memory**（跨会话状态/知识连续性）、**Skills**（可复用能力封装）、**Constraints**（规则/权限/边界）、**Sandbox**（隔离执行环境）
- Vetra 已承载多个联想内部项目：SSG Sales Enablement Agent + IDG CS SW Development Agent（含 Dev Agent、Test Agent 等 6 个子 Agent，Phase 1 2026.6-8 进行中）
- 关键设计边界：Vetra 不替代现有系统（GitLab/Jira/Confluence/测试平台），只做编排、集成、可视化
- 开发策略：Workflow-First → Skill-as-Product → Agent Assembly → Eval-driven Loop
- 知识库方案：Hybrid RAG + PageIndex（结构化可追踪上下文，解决纯语义 RAG 的路径不透明/输出不稳定问题）

---

## 附录：评估维度说明

选择平台时需权衡的关键维度：

| 维度 | 说明 |
|------|------|
| 开发速度 | 多快能从零到第一个可用版本 |
| 定制深度 | 能否满足复杂 operation 场景 |
| 集成广度 | 能接多少内部系统 |
| 维护成本 | 谁维护、需要什么技能 |
| 安全合规 | 数据不出境、权限管控 |
| 用户体验 | 非技术用户能否顺利使用 |
