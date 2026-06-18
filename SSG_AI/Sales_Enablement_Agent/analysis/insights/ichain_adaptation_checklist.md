# iChain 理念适配 SSG Sales Enablement Agent — 信息需求清单

> 创建：2026-06-03 | 更新：基于 SSG Enablement AI Agent.pptx 填充已知信息

---

## 已确认信息（来源：SSG Enablement AI Agent.pptx）

### 1. SSG 销售运营角色（Persona）✅

| 角色 | 说明 |
|------|------|
| **Sales Enablement Team** | 销售赋能团队，计算销售成本、发布、验证 |
| **GPS PM** | 全球产品服务经理 |
| **TMO / SMO** | 技术/解决方案市场运营 |
| **Offering Manager** | 产品经理 |
| **Portfolio Lead** | 产品组合负责人 |
| **Geo Sales Enablement** | 各地区销售赋能 |
| **Finance Team** | 财务团队，计算标准成本 |
| **Pricing Team** | 定价团队，行业研究、PFV 分析、定价 |
| **SA（Solution Architect）** | 解决方案架构师 [待确认] |
| **Service Readiness Team** | 服务就绪团队，评估新 MT 的服务层级 |

### 2. 业务运营闭环 ✅

```
Define Service Tier（定义服务层级）
  ↓
Service PN Enable（扩展/创建服务 PN）
  ↓  ← Consolidate & Validate PN Request
  ↓
Calculate Standard Cost（Finance Team，基于 PH3 加权平均）
  ↓
Calculate Sales Cost（Sales Enablement Team，验证、对标 HW AUR）
  ↓
Calculate List Price / Channel Price（Pricing Team，PFV 对标）
  ↓
Publish（各层级价格发布）
  ↓
Re-Pricing & Cost Update（年度/临时审查，上下调整）
```

### 3. 系统生态 ✅

| 系统 | 用途 |
|------|------|
| **ICP** | MT 信息录入（target price, announce date 等） |
| **SPEP** | PN 半自动创建 |
| **SCFE** | 标准成本加权平均 |
| **CPM** | Sales Cost uplift 规则和计算 |
| **ODT** | 属性变更管理 |
| **Concord Process** | 交易治理流程 |

### 4. 12 个 AI 场景（优先级清单）✅

| # | 场景 | 类型 |
|---|------|------|
| 1 | ODT 属性变更 → 影响/风险分析 + Booking Impact | 分析+预警 |
| 2 | 提交 PN 需求 → 自动生成 POR Excel 或需求表单 | 自动化 |
| 3 | 新 PN 创建前检查重复/筛选可用既有 PN | 检索+判断 |
| 4 | MT 和 Service Tier Announcement 捕获（规则+策略讨论） | 知识捕获 |
| 5 | PN Lifecycle 管理——定期筛选可关闭 PN，发送审批 | 周期性操作 |
| 6 | Sub-Tier 定义——分析 MT target price，确定 sub-tier 归属 | AI 分析 |
| 7 | PN 创建/扩展判断——自动化+默认值填充 | 自动化+判断 |
| 8 | 标准成本数据基础计算 | 计算自动化 |
| 9 | Sales Cost uplift 规则和数值定义 | 规则配置 |
| 10 | PFV 分析——行业研究、竞品价格监控 | AI 研究 |
| 11 | List Price / Channel Price 半自动计算 | 计算自动化 |
| 12 | PN 主数据查询——客制化报告（Booking / 客户维度等） | 知识检索 |

**另外**：新人 Onboarding——GPS PM/TMO/SMO/Offering Manager 的 PN 流程、步骤、场景、审批规则介绍。

### 5. 知识域 ✅

- **PN 主数据**：Material Master、Price & Cost Master
- **Service Tier / Sub-Tier 体系**：层级定义、兼容性、升级路径
- **MT Announcement**：新机型发布信息
- **Booking 数据**：PN 维度的销售数据
- **PFV 基准**：行业竞品价格对标
- **PN Lifecycle 规则**：何时可关闭 PN
- **审批规则**：PN 创建/变更的审批流程
- **流程知识**：PN 创建的完整流程、步骤、场景

---

## 仍需确认的信息

### 6. 使用渠道 ✅

**决策**：设计覆盖全渠道，实施按实际选。

- Teams 对话（快速查询、审批通知）
- Web Persona Workspace（复杂操作、数据面板）
- 嵌入现有系统 SPEP/CPM 内（操作中即时辅助）

> 架构设计为 channel-agnostic（渠道无关），Agent 后端统一，前端适配。

### 7. 数据安全与 LLM 部署 ✅

- **LLM 部署**：SaaS 模式（如 Azure OpenAI / DeepSeek API）
- **Agent 权限模式**：半自动
  - 常规操作（PN 重复检查、数据查询、报告生成）→ Agent 自主执行
  - 涉及成本/价格的操作（Standard Cost、Sales Cost、Pricing）→ 人审批后执行

---

## 架构方向推断（基于已确认信息）

```
SSG Sales Enablement Agent
├── Persona Workspace
│   ├── GPS PM Workspace（PN 创建、生命周期管理、报告查询）
│   ├── Sales Enablement Workspace（Sales Cost 计算、审批、发布）
│   ├── Pricing Workspace（PFV 分析、定价计算）
│   └── Finance Workspace（标准成本计算）
├── Persona Agents
│   ├── PN Creation Agent（场景 2,3,7）
│   ├── Pricing Agent（场景 6,10,11）
│   ├── Cost Agent（场景 8,9）
│   ├── Lifecycle Agent（场景 5）
│   └── RAG Knowledge Pipeline（共享管线，服务所有 Sub-Agent）
└── Tech Stack
    ├── DeerFlow (Vetraflow) — Agent 编排
    ├── Lenovo Hybrid AI Platform — 模型/知识/数据
    └── Systems: ICP / SPEP / SCFE / CPM / ODT / Concord
```
