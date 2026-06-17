# SSG Dynamic Pricing — High-Level 方案设计 V1

> 2026-06-10 | Dynamic Pricing 子项目

---

## 1. 问题定义

在给定 List Price / Channel Price 基准和 HW 交易上下文下，为每笔服务交易确定最优 Sales Price。

**核心约束**：
- 服务附着于硬件 → 硬件价值是服务定价的必要输入
- 服务交付成本随硬件配置变化 → 同一服务在不同硬件上成本不同
- 服务价格不应被硬件折扣等比拖低 → 需要部分解耦

---

## 2. 架构总览

```
                        ┌─────────────────────┐
                        │  Sales Enablement    │
                        │  Agent (主数据层)     │
                        │  List / Channel Price│
                        └──────────┬──────────┘
                                   │
  ┌────────────────────────────────┼──────────────────────────────────┐
  │                      SSG DYNAMIC PRICING ENGINE                    │
  │                                                                    │
  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐    │
  │  │ Feature Store│───→│  Inference   │───→│  Post-Processing │    │
  │  │              │    │  Engine      │    │                  │    │
  │  │ HW 价值 ────┤    │              │    │ Guardrails ──────┤    │
  │  │ 服务特征 ───┤    │ Layer 1:     │    │  ≥ Service Cost  │    │
  │  │ 客户画像 ───┤    │  Rule Engine │    │  ≤ List Price    │    │
  │  │ 历史交易 ───┤    │  (约束区间)   │    │  Max Discount %  │    │
  │  │ 竞争信号 ───┤    │              │    │                  │    │
  │  └──────────────┘    │ Layer 2:     │    │ Delegation ──────┤    │
  │                      │  ML Model    │    │  超阈值 → 人工   │    │
  │                      │  (最优折扣)   │    │  审批            │    │
  │                      └──────────────┘    └────────┬─────────┘    │
  │                                                    │              │
  └────────────────────────────────────────────────────┼──────────────┘
                                                       │
                                                Sales Price
```

---

## 3. 与 PAIDS 的关系

**不替代 PAIDS，不依赖 PAIDS。**

```
PAIDS                         SSG Dynamic Pricing Engine
─────                         ──────────────────────────
定价对象：硬件                  定价对象：附着于硬件的服务
核心变量：组件成本、竞品、Margin  核心变量：HW 价值、服务等级/年限、
                                      客户分层、服务交付成本
输出：HW Transaction Price     输出：Service Sales Price

Interface: PAIDS 输出的 HW Price 是 Feature Store 的一个输入字段
           → 同一笔交易中 HW 和服务的价格来自不同引擎，各算各的
```

**设计决策**：服务引擎独立运行。PAIDS 的 HW 价格是输入特征之一——引擎可以学习「HW 价格对服务最优折扣的预测力」，而不是被 HW 价格机械绑定。

---

## 4. Inference Engine 设计

### 4.1 Layer 1: Rule Engine（约束区间）

输出：服务 Sales Price 的可行区间 `[P_min, P_max]`

```
P_min = max(Service_Cost, List_Price × Min_Discount_Floor)
P_max = min(List_Price, Channel_Price)
```

附加规则：
- HW 价值分段折扣上限（$0-1000 / $1000-2000 / $2000+ 各自不同的 Max Discount %）
- 服务合同期限系数（3 年 > 1 年享更高折扣上限）
- 特定客户/GEO 的协商价覆盖

### 4.2 Layer 2: ML Model（最优折扣）

在 Rule Engine 给出的 `[P_min, P_max]` 区间内，推荐最优价格点。

**候选模型方向**：

| 模型 | 适用场景 | 数据需求 |
|------|---------|---------|
| **Price Elasticity Model** | 交易量大、价格变化频繁 | 历史成交价格 + 成交量 |
| **Contextual Bandit** | 需要在线探索最优折扣 | 实时成交/未成交反馈 |
| **Causal ML (Uplift Model)** | 估计「折扣 → 成交概率」因果效应 | 成交/未成交 + 折扣 + 特征 |
| **Gradient Boosting (XGBoost/LightGBM)** | 快速启动，特征工程驱动 | 历史成交数据 + 标签 |

**推荐路径**：
- Phase 1：Rule Engine 单独运行（不需要训练数据）
- Phase 2：Rule Engine + XGBoost（用历史数据训练折扣推荐模型）
- Phase 3：Causal ML / Bandit（积累足够反馈数据后升级）

### 4.3 Layer 3: Post-Processing

- **Guardrails**：不低于 Service Cost、不高于 List Price
- **Delegation**：折扣超过阈值 → 推人工审批（复用 PAIDS Dynamic Delegation 模式）
- **Audit Log**：每笔推荐记录输入特征、模型版本、输出价格、是否被人工覆盖

---

## 5. 数据需求

| 数据 | 来源 | 必要性 |
|------|------|--------|
| List Price / Channel Price | Sales Enablement Agent 主数据 | 必须 |
| HW 交易价格 | PAIDS 或交易系统 | 必须 |
| HW 属性（CPU/GPU/Memory/系列） | LPC / 交易系统 | 必须 |
| 服务 Tier / Term / SLA | 服务主数据 | 必须 |
| Service Cost（交付成本） | 财务/运营系统 | 推荐 |
| 客户分层 / 行业 | CRM | 推荐 |
| 历史服务成交价 + 成交量 | 交易系统 | Phase 2+ 需要 |
| 竞品服务价格 | 市场情报 | Phase 3+ 可选 |

---

## 6. 落地路径

```
Phase 1: Rule Engine Only（4-6 周）
├── 实现 Layer 1（约束区间）+ Layer 3（Guardrails）
├── HW 价值分段 × 服务 Tier 的折扣上限矩阵
├── 输出：可行价格区间 + 人工选择
└── 价值：即时有可用服务定价，零数据依赖

Phase 2: Rule + ML（6-10 周）
├── 积累 2-3 个月交易数据后
├── XGBoost 模型：输入 HW 价值 + 服务特征 + 客户特征 → 推荐折扣
├── 模型在 Rule 约束区间内输出最优价格点
└── 价值：自动化折扣推荐，人工审批率逐步降低

Phase 3: Causal ML / Online Learning（Phase 2 稳定后）
├── 升级为 Contextual Bandit 或 Uplift Model
├── 在线学习最优折扣策略
├── 引入服务竞争信号
└── 价值：持续优化，接近全自动
```

---

## 7. 与 Sales Enablement Agent 的接口

```
Sales Enablement Agent              Dynamic Pricing Engine
──────────────────────              ─────────────────────
产出 List Price / Channel Price  →  作为 P_max 的上限约束
  （主数据层，定期发布）                作为特征输入之一

                                  →  产出 Sales Price
                                      （交易层，每笔交易）
```

两个 Agent 独立运行，通过主数据接口解耦。Sales Enablement Agent 不需要知道 Dynamic Pricing 的存在——它只管发布基准价格。

---

## 8. 关键设计决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 与 PAIDS 的关系 | 独立引擎，PAIDS HW 价格为输入 | 服务定价需要独立优化空间，不被 HW 定价绑定 |
| 引擎架构 | Rule + ML 混合 | 行业标准，PAIDS 已验证 |
| 启动策略 | Rule Only → +ML → +Causal | 零数据依赖起步，逐步智能化 |
| 审批机制 | 超阈值 → 人工审批 | 风险可控，渐进信任 |
| 数据需求最低门槛 | HW 价值 + 服务 Tier + List Price | 3 个字段即可 Phase 1 运行 |
