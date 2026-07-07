# SSG Dynamic Pricing — B2B 服务交易价格动态优化 V3

> 2026-07-07 | Dynamic Pricing 子项目
> 面向业务决策层 | Wave 1 聚焦 B2B (LBPi + LBPe)

---

## 1. 一句话定位

**做 Dynamic Pricing——让服务的价格跟着硬件的价格走。**

在 B2B 商机→报价→合同→订单的销售流程中（覆盖 LBPi 直销 + LBPe 渠道），当销售配置完硬件 + 服务后，系统自动输出每项服务 PN 的 **Price Band（Floor / Target / Stretch）+ Reason Code + Confidence Level**。推荐价随 HW 价格联动：HW 涨价服务价跟涨，HW 降价则自动上调 Pen Rate，确保服务收入不因 HW 打折被等比拖低。

**范围**：B2B Direct（LBPi + ISO Sales）和 Channel B2B（LBPe + Channel Partner）。引擎框架设计为渠道无关——eCommerce、Consumer/SMB、Renewal 等方向由同一引擎支撑，本次不展开。

---

## 2. 为什么现在必须做

### 2.1 现状：同一 Service Tier 下，不同 HW 的价格差异被忽略

当前服务定价以 Service Tier 为主要维度：3 年 Premier Support 对所有 HW 型号收取相同的 Pen Rate（如均为 HW 渠道价的 8%）。但同一个 Tier 下，不同 HW 的 PFV（Product Fair Value，产品市场参考价）和交付成本可能差距极大：

| 对比 | ThinkPad X1 Carbon | ThinkBook 14 | 差异 |
|------|-------------------|-------------------|------|
| HW 渠道价 | $2,000 | $800 | **2.5×** |
| 3yr Premier Support（Pen Rate 8%） | $160 | $64 | **2.5×** |
| 实际服务交付成本差异 | ~1.5× | — | 远小于价格差 |
| **结果** | Margins 可能偏低（服务定价未反映高 HW 价值） | Margins 偏高但竞争力弱 | **两个方向都在漏利润** |

**问题本质**：同一个 Service Tier 用一个 Pen Rate 覆盖所有 HW，忽略了 HW 之间的 PFV 和成本差异——高价值 HW 上服务定价不足（margin leakage），低价值 HW 上可能竞争力不足。

### 2.2 目标：让服务价格反映 HW 的价值差异

| 场景 | 当前（固定 Pen Rate） | 方案实施后（动态引擎） |
|------|---------------------|----------------------|
| 高 PFV HW | 服务价被 Pen Rate 锁死，无法充分捕获 HW 价值 | Pen Rate 适度上调，Price Band 反映实际 HW 价值 |
| 低 PFV HW | 服务价绝对值低但竞争力不足 | Pen Rate 灵活调整，在 Margin Floor 之上找最优平衡 |
| HW 降价 10% | 服务收入等比缩水 | 引擎上调 Pen Rate，服务收入不被等比拖低 |
| 新客群冷启动 | 按全局平均 Pen Rate | 引擎通过 Comparable Benchmark 借用相似客群经验 |

---

## 3. 方案设计

### 3.1 核心公式

```
Maximize Expected Profit = Conversion Probability × (Net Price − Service Cost − Sales Cost)
```

引擎的优化目标不是简单的"Pen Rate 最大化"——是**在保证成交概率的前提下最大化单笔利润**。三个约束：

1. **不亏**：Net Price ≥ Service Cost + Sales Cost（Margin Floor）
2. **合理**：Net Price ≤ List Price
3. **可控**：超 DOA 阈值的推荐自动标记，推人工审批

### 3.2 四维输入

引擎基于四个维度学习最优定价：

| 维度 | 字段 | 说明 |
|------|------|------|
| **HW Context** | HW Config / HW Cost / HW Price / PFV | 被定价的硬件是什么、值多少、竞品价多少 |
| **Service Economics** | SVS Cost / Sales Cost / List Price / Margin Target | 交付成本、销售成本、定价基准、利润率目标 |
| **Deal Context** | Country/Geo / Segment / Deal Size | 谁在买、在哪买、单多大 |
| **Historical Behavior** | Quote / Contracts / Orders / Win-Loss / Pen Rate | 类似客户历史上接受了什么价格 |

### 3.3 六步引擎流水线

```
Request Intake & Feature Assembly
        │
        ▼
Comparable Benchmark（accept price range / pen rate / win-loss pattern）
        │
        ▼
Generate Candidate Price Options
        │
        ▼
Price Scoring（Conversion Probability × Expected Profit）
        │
        ▼
Apply Guardrails（Margin Floor / Local Policy / Contract Restriction / Exception Rule）
        │
        ▼
Generate Reason Code + Confidence Level
        │
        ▼
Price Band：Floor / Target / Stretch
```

**每步说明**：

| 步骤 | 做什么 |
|------|--------|
| **Request Intake & Feature Assembly** | 接收报价请求，组装四维特征 |
| **Comparable Benchmark** | 检索相似交易（同 HW 价值段 × Tier × GEO × 客户段）的历史成交价格带、Pen Rate 分布、赢单/丢单模式 |
| **Generate Candidate Prices** | 基于 Benchmark + 当前 Deal Context 生成多个候选 Pen Rate 及对应价格 |
| **Price Scoring** | 对每个候选价估算 Conversion Probability × Expected Profit，排序 |
| **Apply Guardrails** | 逐层校验：Margin Floor → Local Policy → Contract Restriction → Exception Rule |
| **Generate Reason Code + Confidence** | 输出推荐理由和置信度，低置信标记 DOA 审批 |

**输出**：Price Band 三档

| 档位 | 含义 | 业务场景举例 |
|------|------|------------|
| **Floor** | 保底价——低于此价不卖 | 竞品压价时销售的谈判底线 |
| **Target** | 推荐价——引擎认为的最优平衡点 | 默认填入报价单的值 |
| **Stretch** | 溢价——客户对价格不敏感时争取的上限 | 大单、独供、紧急需求 |

每档附带 **Reason Code**（为什么推荐这个价格）和 **Confidence Level**（引擎有多确定）。

### 3.4 Foundation 层

引擎依赖以下基础能力，在 Wave 1 中一并建设：

```
┌─────────────────────────────────────────────────────┐
│                  Foundation Layer                    │
├──────────────┬────────────────┬─────────────────────┤
│ Data Readiness│Feature         │Comparable Benchmark │
│ (Integration │Engineering     │(accept price range  │
│ · Cleansing  │· Pricing Signal│· pen rate · win/loss│
│ · Standard.) │· HW Value Tier │ pattern)            │
├──────────────┼────────────────┼─────────────────────┤
│ Price Response│Pricing         │Margin & Cost Model  │
│ Model        │Guardrail       │                     │
│ (conversion  │· Margin Floor  │(SVS cost · sales    │
│ probability) │· Local Policy  │ cost · target margin│
│              │· Contract Rest.│· expected profit)   │
└──────────────┴────────────────┴─────────────────────┘
```

---

## 4. 设计原则

| 原则 | 说明 |
|------|------|
| **学习而非预设** | Pen Rate 不从人工规则表查，从历史交易数据中学——系统自动发现「$2,000 的 X1 Carbon × 3yr Premier Support × EMEA × Enterprise」的最优 Price Band |
| **独立于 HW 定价** | Dynamic Pricing 引擎不与 PAIDS（HW 定价系统）耦合。PAIDS 输出的 HW 价格只是引擎的 HW Context 输入之一——引擎独立决策服务 Price Band，不被 HW 定价策略绑定 |

---

## 5. 落地节奏

### 5.1 核心原则：渐进信任

信任不是一次性交付的，是逐步建立的。每一个阶段都可回退。

```
POC 离线验证 → Pilot 推荐参考 → Rollout 嵌入流程
  零风险          低风险             中低风险
```

### 5.2 三阶段交付

| | POC | Pilot | Rollout |
|---|---|---|---|
| **时间** | 2 个月 | 3 个月 | 1 个月 |
| **范围** | 1 个 GEO（EMEA）+ 3 个 Service Tier | 全部 GEO + 全部 Tier | LBPi + LBPe 全量 |
| **技术交付** | 离线跑通引擎流水线（6 步），产出 Price Band 推荐表，与历史人工成交价逐笔对比 | 引擎接入报价工具，销售在报价界面看到「AI Price Band」字段 | Price Band 自动填入报价单，销售确认或修改即可 |
| **业务流程** | 不改变销售流程 | 试点销售团队新增 Price Band 字段，追踪采纳率和偏离度 | Target 自动填充，超 DOA 修改需记录原因 |
| **业务 KPI** | 输出「AI vs 人工」偏差分析报告 | 采纳率追踪（Target 采纳 + Floor/Stretch 使用率） | 采纳率、偏离度纳入日常 KPI |
| **团队准备** | 无需培训 | 1 次 15 分钟销售培训 | IT 嵌入报价工具（开发+UAT） |
| **风险** | 🟢 零风险：离线实验 | 🟡 低风险：推荐仅参考，销售保留决定权 | 🟡 中低：嵌入流程但保留人工覆盖 |

### 5.3 月度路线图（6 个月投产）

| 月 | 阶段 | 里程碑 |
|---|---|---|
| M1 | POC | 数据接入完成（HW Price / Service Cost / 历史交易 / CRM 客户分层），Data Readiness 达标 |
| M2 | POC | 引擎流水线跑通，产出第一版 Price Band 推荐表，完成「AI vs 人工」偏差分析报告 |
| M3 | Pilot | 报价工具完成 API 对接，试点销售团队（5-10 人）开始使用 AI Price Band 推荐 |
| M4 | Pilot | 收集采纳率数据，迭代引擎参数，优化低置信场景的 Guardrail 阈值 |
| M5 | Pilot | 全 GEO + 全 Tier 覆盖，采纳率目标 ≥ 60%，启动 Rollout 准备 |
| M6 | Rollout | LBPi + LBPe 全量嵌入，Target 自动填充，超 DOA 修改记录原因，日常 KPI 上线 |

---

## 6. 业务效果量化

### 6.1 直接指标

| 指标 | 当前 | 目标 | 验证方式 |
|------|------|------|---------|
| 新 GEO 冷启动推荐精度 | 全局均值（一刀切） | 优于全局均值 30%+ | 留一法交叉验证 |
| Price Band 采纳率 | — | Pilot 期 ≥ 60% | 报价工具埋点统计 |
| $/HW 波动率 | 随 HW 价格等比波动 | 波动幅度缩小 50%+ | 季度对比 |

### 6.2 三个典型场景

**场景 1：HW 大单降价，服务利润不崩**

某大客户 EMEA 区，ThinkPad 企业采购大单 HW 折扣 15%。当前：所有服务 PN 的 Sales Price 被等比压低 15%（因为 Pen Rate 固定）。方案后：引擎识别该客户段的 $/HW 目标，输出上调后的 Pen Rate，Price Band 的 Floor 仍守住 Margin Floor，服务收入不被 HW 折扣等比拖低。

**场景 2：HW 涨价，释放 space 抢 attach**

某产品线 HW 供不应求，渠道价上涨 8%。当前：服务价跟涨 8%（客户已在 HW 上多付，再加价易引发抵触）。方案后：引擎输出适度下调 Pen Rate 的 Price Band，Target 服务价仅涨 5%，降低客户总拥有成本感知，提升服务 attach 率。

**场景 3：新 GEO 冷启动，不拍脑袋**

AP 新市场数据积累不足，当前只能按全局 Pen Rate 报价。方案后：Comparable Benchmark 自动收缩到相似 GEO（EMEA）的先验 price range 和 win-loss pattern，推荐精度高于全局一刀切。Confidence Level 自动标记为 Low，提示销售谨慎使用。

---

## 7. 数据与团队

### 7.1 数据需求

| 数据 | 来源 | 引擎对应维度 |
|------|------|:--:|
| HW Channel Price / PFV | PAIDS 或交易系统 | HW Context |
| HW Config / HW Cost | 产品主数据 | HW Context |
| 服务 Tier × Term × SLA | 服务主数据 | Service Economics |
| Service Cost / Sales Cost | 财务/运营系统 | Service Economics |
| List Price / Margin Target | 定价系统 (CPM) | Service Economics |
| 历史 Quote / Contracts / Orders / Win-Loss | CRM / LBP | Historical Behavior |
| 历史 Pen Rate | SSR 数据 | Historical Behavior |
| GEO / Segment / Deal Size | CRM | Deal Context |
| 报价工具 API（Price Band 回填） | LBPi / LBPe | 输出 |

### 7.2 团队配合

| 阶段 | 角色 | 投入 |
|------|------|------|
| POC | 数据工程师（1 人） | 2 周数据清洗 + 特征工程 |
| Pilot | 报价工具开发（1 人）、销售试点团队（5-10 人） | 3 个月 |
| Rollout | IT 集成开发（2 人）、全量销售培训 | 1 个月 |

---

## 8. 未来拓展

Wave 1 交付 B2B 引擎后，同一引擎框架可横向复用到其他渠道——不是把 B2B 做更深，而是把已验证的引擎搬到新场景：

| 拓展方向 | 渠道 | 场景 |
|---------|------|------|
| eCommerce | Consumer/SMB 自助购买 | 服务推荐嵌入线上购买流程 |
| Channel RunRate | ESS / 4P | 渠道跑量场景的批量定价 |
| APOS Renewal | LBP | 续约/升级场景的差异化定价 |

每个新方向复用同一条六步流水线——换的是输入维度的权重（如 eCommerce 更侧重 Conversion Probability，Renewal 更侧重 Historical Behavior），不换引擎架构。

---

## 9. 结论

> **做 Dynamic Pricing——让服务的价格跟着硬件的价格走，而不是被硬件价格牵着走。**

6 个月可投产的路径：POC 离线验证 → Pilot 给人用 → Rollout 嵌入 LBPi + LBPe。不动现有定价体系，在报价环节加一层引擎推荐——销售看到的是 Price Band（Floor / Target / Stretch），有 Reason Code 知道为什么，有 Confidence Level 知道该不该信。未来从 B2B 出发，同一引擎支撑更多渠道。
