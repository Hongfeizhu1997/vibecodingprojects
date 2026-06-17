# Dynamic Pricing 行业 Pre-Study（更新版）

> 2026-06-10 | 来源：Wikipedia API + Semantic Scholar + Agent 训练知识
> 标注：[V] = 外部来源已验证 | [K] = Agent 训练知识 | [?] = 待验证

---

## 一、行业实践：IT 硬件厂商如何为附属服务定价

### 1.1 核心发现：行业共识是「按 HW 价格百分比」

Wikipedia 对 Extended Warranty 的定义 [V]：

> "Extended warranties cost extra and for a **percentage of the item's retail price**."

这说明按 HW 价格百分比为服务定价是全行业的基线做法。方案 A（Pen Rate）并非联想独创，而是业界通行的起点。

### 1.2 AppleCare [K]

| 维度 | 实践 |
|------|------|
| 定价模式 | 按设备类别固定价格。Mac $99-379，iPhone $149-269 [?] |
| 与 HW 价值关系 | 比率接近但不固定——$2000 MBP AppleCare+ ~$379（~19%），$999 MBA ~$199（~20%） |
| 是否动态 | ❌ 静态 |
| 关键维度 | 设备类别、屏幕尺寸、维修率 |

### 1.3 Dell ProSupport [K]

| 维度 | 实践 |
|------|------|
| 定价模式 | 产品系列 × 服务等级 × 年限矩阵 |
| 与 HW 价值关系 | 百分比基准——Latitude 和 Precision 费率不同 |
| 是否动态 | 部分——大客户有议价空间 |
| 关键维度 | 产品系列、服务等级、年限、客户规模、渠道 |

### 1.4 HP Care Pack [K]

| 维度 | 实践 |
|------|------|
| 定价模式 | 产品系列 × 覆盖等级 × 年限矩阵 |
| 特殊点 | Post-Warranty 购买价格高于随设备购买 |

### 1.5 行业变量共识 [K]

| 变量 | 行业采用度 | 实现复杂度 |
|------|---------|-----------|
| HW 价值（产品系列/价格段） | ⭐⭐⭐⭐⭐ 全行业 | 低 |
| 服务等级 | ⭐⭐⭐⭐⭐ 全行业 | 低 |
| 合同年限 | ⭐⭐⭐⭐ 主流 | 低 |
| 购买时机（随设备/Post-Warranty） | ⭐⭐⭐ 常见 | 低 |
| 客户规模/行业 | ⭐⭐⭐ 大客户场景 | 中 |
| 渠道差异 | ⭐⭐⭐ 常见 | 低 |

---

## 二、学术文献

### 2.1 经典理论 [V]

| 理论 | 来源 | 核心观点 |
|------|------|---------|
| **价格歧视** | Wikipedia [V] | 相同/相似商品按不同细分市场定价。依赖客户支付意愿差异和需求弹性差异 |
| **Product-Service System** | Wikipedia [V] | PSS 是产品与服务协同交付的商业模式，正成为协同消费的使能手段 |
| **动态定价** | Wikipedia [V] | 按当前市场需求灵活定价。高峰期提价，低谷期降价 |

### 2.2 关键论文 [V]

| 论文 | 年份 | 核心内容 |
|------|------|---------|
| **On Bundling and Pricing of the Service with the Product** | 2007 | Kameshwaran, Viswanadham, Desai。直接研究服务与产品捆绑定价——这是方案 A vs B 之争的理论源头 |
| **A pricing optimization modelling for assisted decision making in telecommunication product-service bundling** | 2024 | 电信产品-服务捆绑的定价优化模型 |
| **Bundling Variety, Usage, or Both?** | 2024 | 多服务分析：Pay-Per-Use vs 订阅定价。整合产品捆绑与使用量定价 |
| **Generative AI For Personalized Product Bundling** | 2025/2026 | GenAI 用于个性化产品捆绑的收益/利润优化框架 |

### 2.3 理论启示 [K]

| 理论 | 对 SSG 的指导 |
|------|-------------|
| **捆绑定价理论** (Adams & Yellen 1976; Schmalensee 1984) | 当客户对 HW 和服务的估值分布不同时，混合捆绑（可拆开买）优于纯捆绑。→ 服务价格不应与 HW 强耦合 |
| **服务异质性** (Zeithaml et al.) | 同是 Premier Support，服务高配设备的交付成本更高 → 服务定价应反映交付成本差异，不仅是 HW 价值百分比 |
| **Causal ML** | 如果有服务成交/未成交 + 折扣数据，可直接估计「折扣对成交概率的因果效应」→ Uplift Modeling |

---

## 三、定价引擎架构

### 3.1 行业通用模式 [K]

```
FEATURE STORE → INFERENCE ENGINE → POST-PROCESSING → PRICE OUTPUT
  (实时+批量)    (Rule+ML混合)       (Guardrails/审批)
```

分层推理：

```
Layer 1: Rule Engine — 硬约束（不低于成本、不高于 List Price）+ 业务规则
Layer 2: ML Model — 价格弹性 / 竞品对标 / 优化折扣
Layer 3: Post-Processing — Guardrails / Delegation / 审批
```

这与 PAIDS 架构一致。

### 3.2 Feature Store 设计参考 [K]

| 特征类别 | 示例 | 更新频率 |
|---------|------|---------|
| HW 属性 | Price, CPU/GPU/Memory, Age | 每日 |
| 服务属性 | Tier, Term, SLA | 准静态 |
| 客户属性 | Segment, Industry, History | 每周 |
| 交易上下文 | Channel, Region, Deal Size | 实时 |
| 竞争信号 | Competitor Price, Win/Loss | 每日/每周 |
| 历史统计 | Avg Discount, Win Rate | 每日 |

---

## 四、对 SSG Dynamic Pricing 的更新启示

| # | 发现 | 来源 | 指导 |
|---|------|------|------|
| 1 | 按 HW 价格百分比为服务定价是**全行业基线** | Wikipedia [V] | 方案 A 是行业共识起点，不是联想特例 |
| 2 | 但学术上「捆绑定价」理论认为服务应**部分独立** | 2007 论文 [V] + 捆绑理论 [K] | 方案 B 有理论支撑 |
| 3 | 服务交付成本随 HW 配置变化 | 服务异质性理论 [K] | 定价模型需 HW 组件级特征 |
| 4 | 2024-2026 的论文开始用 GenAI 做个性化捆绑 | S2 论文 [V] | 前沿方向——不只是规则+ML，LLM 也可能参与 |
| 5 | PSS（Product-Service System）是学术共识框架 | Wikipedia [V] | SSG 的业务本质上就是 PSS |
| 6 | Rule+ML 混合是定价引擎行业标准 | 架构模式 [K] + PAIDS | 不造新轮子 |

---

## 五、待外部验证

1. [ ] 2007 年论文 "On Bundling and Pricing of the Service with the Product" 全文——直接相关
2. [ ] Dell/HP 当前服务费率的具体数值（需实时搜索或内部竞品数据）
3. [ ] AWS/Azure RI 定价模型对服务合同期限的参考价值
4. [ ] SSG 内部服务交付成本是否确实随 HW 配置上升（数据验证）
