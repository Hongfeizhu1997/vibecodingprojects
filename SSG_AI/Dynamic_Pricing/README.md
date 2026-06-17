# SSG Dynamic Pricing — AI 驱动的服务交易价格动态优化

> SSG AI 子项目 #3 | 联想 SSG (Solutions & Services Group)
> 侧重：模型选型 · 竞品调研 · 方案设计

---

## 定位

面向 SSG GPS 服务 PN 的**最终交易售价（Sales Price）**。与 Sales Enablement Agent 的分工：

```
Sales Enablement Agent (主数据层)        Dynamic Pricing (交易层)
─────────────────────────────            ─────────────────────
List Price / Channel Price                Sales Price = 基准价 − 折扣
定期发布，人工审批 + Agent 辅助             每笔交易，模型驱动
         ↓                                       ↓
         作为 Dynamic Pricing 的主数据输入        最终报价
```

---

## 核心洞察：服务 Dynamic Pricing ≠ 硬件 Dynamic Pricing

联想已有成熟硬件定价引擎 **PAIDS**（Pricing AI Decision System，2023 年自研上线，替代第三方服务商，年省 $1.25M）。PAIDS 2.0 正在加入 **SSG Pen Rate Pricing**——这是服务定价的起步，但服务定价有一个硬件定价不存在的核心维度：

> **服务附着在硬件上。同一服务，硬件价值不同 → 成本不同 → 客户收益不同 → 价格应不同。**

| 维度 | 硬件 Dynamic Pricing | 服务 Dynamic Pricing |
|------|---------------------|---------------------|
| 定价对象 | 硬件本身（ThinkPad / ThinkSystem） | 附着于硬件的服务（保修 / 支持 / 部署） |
| 核心变量 | 组件成本、竞品价格、Margin 目标 | **硬件价值、Pen Rate、服务成本、客户收益** |
| 价格-硬件关系 | 无关（硬件就是被定价的对象） | **正相关**——$2000 PC 的服务 > $1000 PC 的同等服务 |
| 成本驱动 | BOM 成本 | 服务交付成本（随硬件复杂度上升）+ 风险敞口 |
| 已有系统 | PAIDS（成熟） | PAIDS 2.0 SSG Pen Rate（起步） |

**举例**：同是 3 年 Premier Support，配 ThinkPad X1 Carbon ($2,000) vs ThinkPad E 系列 ($800)。联想的服务成本、客户的时间价值、硬件风险敞口都不同——服务价格应反映这些差异。

---

## PAIDS 现有能力（参考基线）

从 PAIDS 架构和 2.0 规划中提取的相关能力：

| PAIDS 能力 | 说明 | 对服务 DP 的参考价值 |
|-----------|------|-------------------|
| **Inference Engine** | 核心定价推理引擎 | 服务 DP 可复用架构模式 |
| **Dynamic Delegation** | 分层审批 + Guardrail 阈值 | 服务 DP 的风险控制机制 |
| **Multi-level Clustering** | 6 级产品聚类 → 推断匹配 | 服务-HW 组合的分群定价 |
| **Dynamic Expert Rules** | 每市场 5 维特征规则 | 服务 DP 的规则层设计参考 |
| **SSG Pen Rate Pricing** 🆕 | 服务渗透率定价（PAIDS 2.0 新增） | **最近的起点**——但仅 Pen Rate 一个维度，需扩展 |
| **Component Cost Adjustment** | 组件级成本调整（Memory/CPU/GPU） | 可类比：服务定价引入 HW 组件价值权重 |

---

## 关键设计问题

1. **HW 价值如何量化进服务价格？** HW AUR？HW 组件价值（CPU/GPU/Memory）？还是 HW Channel Price 的百分比？
2. **Pen Rate 之外还需要哪些服务特征？** 服务 Tier、合同期限、客户规模、历史续约率？
3. **与 List Price / Channel Price 的关系？** Sales Price 是 List Price 的折扣？还是独立模型输出？
4. **PAIDS 的 SSG Pen Rate Pricing 能做到什么程度？** 我们是补 PAIDS 的不足，还是独立设计服务 DP 模块？

---

## 探索范围

### 模型选型
- 价格弹性模型（Price Elasticity of Demand）
- 分层定价（Tiered Pricing by HW segment）
- Causal Inference（HW 价值对服务价格因果效应估算）
- Contextual Bandit / RL（在线学习最优折扣）
- 参照 PAIDS 的 Multi-level Clustering + Expert Rules 混合架构

### 竞品调研
- PAIDS SSG Pen Rate Pricing 的详细能力（需内部资料）
- 同行服务定价实践：Dell ProSupport、HP Care Pack、AppleCare
- 学术界：服务定价 × 产品价值关联模型

### 方案设计
- 服务 DP 的数据流：HW 价值 → 服务特征 → 折扣模型 → Sales Price
- 与 Sales Enablement Agent（主数据）和 PAIDS（硬件定价）的接口
- 落地路径与 Guardrail 设计

---

## 项目结构

```
Dynamic_Pricing/
├── README.md
├── research/           # 研究原材料
│   ├── papers/         #   学术论文
│   ├── articles/       #   行业文章
│   └── reports/        #   行业报告
├── analysis/           # 分析产出
│   ├── benchmarks/     #   竞品对标
│   ├── models/         #   模型分析
│   └── insights/       #   洞察总结
├── outputs/            # 最终交付物
│   ├── decks/          #   PPT
│   ├── reports/        #   方案书/白皮书
│   ├── infographics/   #   信息图
│   └── diagrams/       #   架构图
├── notes/              # 工作笔记
└── references/         # 参考资料
    ├── PAIDS Solution and System Architecture.pptx
    └── EA Review - LI2500080-Apex-PAIDS.pptx
```

---

## 技术底座

- PAIDS 提供硬件定价推理能力和 SSG Pen Rate Pricing
- Sales Enablement Agent 提供 List Price / Channel Price 主数据
- DeerFlow (Vetraflow) + Lenovo Hybrid AI Platform 提供基础设施
- Dynamic Pricing 模型层独立——传统 ML（Elasticity / Causal ML）或 Bandit/RL

---

## 当前状态

🆕 项目初始化 | 已通读 PAIDS 参考材料 | 待确认方向

## 待确认

1. PAIDS SSG Pen Rate Pricing 的详细设计文档能否获取？——决定我们是补 PAIDS 还是独立设计
2. HW 价值用哪个指标量化？HW AUR？Channel Price？还是组件级（CPU/GPU/Memory）价值分解？
3. 交易数据来源：Sales Price 成交记录在哪个系统？
