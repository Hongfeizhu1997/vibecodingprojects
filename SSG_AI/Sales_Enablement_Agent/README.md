# SSG Enablement Agent — AI 驱动的 SSG 销售运营赋能

> SSG AI 子项目 #2 | 联想 SSG (Solutions & Services Group)
> 侧重：方案探索 · Agent 设计 · 知识积累

---

## 定位

面向 SSG GPS（Global Product Services）业务团队，构建 AI Agent 辅助服务 PN 全生命周期管理——从 Service Tier 定义、PN 创建、成本核算、定价对标到生命周期管理和数据查询。与 ISG SSR 无关，属独立探索方向。

- **业务线**：SSG GPS
- **核心场景**：服务 PN（Part Number）的创建、定价、成本、生命周期管理
- **设计理念**：借鉴 iChain Persona Workspace & Agent 框架
- **技术底座**：DeerFlow (Vetraflow) + Lenovo Hybrid AI Platform
- **产出物**：方案设计、技术架构、落地路径

---

## 技术栈

```
┌──────────────────────────────────────────┐
│  iChain 设计理念（Persona Workspace）      │  ← 上层模式
├──────────────────────────────────────────┤
│  DeerFlow / Vetraflow（Agent 编排引擎）    │  ← 技术底座
├──────────────────────────────────────────┤
│  Lenovo Hybrid AI Platform               │  ← 基础设施
│  (Models / Knowledge / Data / Tools)      │
├──────────────────────────────────────────┤
│  ICP / SPEP / SCFE / CPM / ODT / Concord │  ← 业务系统
└──────────────────────────────────────────┘
```

---

## 与已有项目的关系

| 维度 | ISG SSR | Sales Enablement Agent（本项目） |
|------|---------|-------------------------------|
| 视角 | 智能服务推荐方案探索 | SSG 销售运营赋能 |
| 面向 | ISG 服务推荐 | SSG GPS 服务 PN 管理 |
| 内容 | 推荐模型设计、知识沉淀 | Persona Agent 架构、PN 操作自动化 |
| 技术底座 | 独立模型 | DeerFlow + Lenovo Hybrid AI Platform |
| 设计参考 | — | iChain Persona Workspace 模式 |
| 输出 | 方案书、白皮书、信息图 | 方案设计、技术架构、落地路径 |
| 状态 | 🔄 进行中 | 🔄 信息收集中 |

---

## 业务范围

### 涉及角色
- Sales Enablement Team / GPS PM / TMO / SMO
- Offering Manager / Portfolio Lead / Geo Sales Enablement
- Finance Team / Pricing Team / Service Readiness Team

### 涉及系统
- ICP（MT 信息管理）
- SPEP（PN 半自动创建）
- SCFE（标准成本计算）
- CPM（Sales Cost 管理）
- ODT（属性变更）
- Concord Process（交易治理）

### 12 个 AI 场景（优先级从 SSG Enablement AI Agent.pptx）
1. ODT 属性变更影响分析 + Booking Impact
2. PN 需求自动生成 POR Excel / 需求表单
3. 新 PN 重复检查 / 既有 PN 筛选
4. MT & Service Tier Announcement 捕获
5. PN Lifecycle 管理（筛选可关闭 PN + 审批）
6. Sub-Tier 定义（MT target price → sub-tier 归属分析）
7. PN 创建/扩展判断自动化 + 默认值填充
8. 标准成本数据基础计算
9. Sales Cost uplift 规则和数值定义
10. PFV 行业研究和竞品价格监控
11. List Price / Channel Price 半自动计算
12. PN 主数据查询（客制化报告、Booking 查询）
13. 新人 Onboarding（PN 流程、场景、审批规则）

---

## 项目结构

```
Sales_Enablement_Agent/
├── README.md
├── research/           # 研究原材料
│   ├── papers/         #   学术论文
│   ├── articles/       #   行业文章
│   └── reports/        #   行业报告
├── analysis/           # 分析产出
│   ├── benchmarks/     #   竞品对标
│   ├── models/         #   分析模型/框架
│   └── insights/       #   洞察总结
│       ├── platform_evaluation.md          # 平台方案评估
│       └── ichain_adaptation_checklist.md  # iChain 理念适配清单
├── outputs/            # 最终交付物
│   ├── decks/          #   PPT
│   ├── reports/        #   方案书/白皮书
│   ├── infographics/   #   信息图
│   └── diagrams/       #   架构图/流程图
├── notes/              # 工作笔记
└── references/         # 参考资料
    ├── Vetraflow wukong.pptx           # DeerFlow 内部评估方案
    ├── iChain Persona Workspace.pdf    # 供应链 AI 助手参考
    └── SSG Enablement AI Agent.pptx    # 业务需求文档
```

## 当前状态

✅ 所有 7 个信息维度已确认
✅ 架构方案 V1 已产出 → `analysis/insights/architecture_v1.md`
✅ 平台评估完成 → `analysis/insights/platform_evaluation.md`
✅ iChain 适配清单完成 → `analysis/insights/ichain_adaptation_checklist.md`

## 下一步

1. 评审架构方案 V1，确认方向
2. 确认系统 API 可用性（ICP/SPEP/SCFE/CPM/ODT/Concord 能否被 Agent 调用）
3. 产出 Wave 1 MVP 详细设计（Knowledge Pipeline + Teams Bot）
