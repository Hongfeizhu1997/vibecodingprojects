# IDG Dynamic Pricing Business Case 分析

> 数据源：`IDG Premier DP Business Case 9.30.xlsb`（财务模型）+ `IDG DP Business Case 9.29.pptx`（executive summary）
> 分析日期：2026-10-08 ｜ 状态：**暂时结论，等财务确认口径**

---

## 一、Business Case 概览

**核心主张**：IDG 采用对标 Dell 的 Pen Rate 目标（动态定价），带来 **$80M–$204M 增量 bookings（$17–$25/CA）**。

- 收益几乎全部来自 **Premier**（Upgrades & Extensions 仅 1,403 行，可忽略）
- Scope：商用产品（NB/DT/WS）、ESS 服务（Premier + U&E）、Standard & Custom PN

---

## 二、核心数字（已验证）

### DP Benefit（Premier）分 Geo

| Geo | Standard PN | CPN | 合计 | 占比 |
|-----|------------|-----|------|------|
| AP | −$0.17M | $1.19M | **$1.03M** | 0.5% |
| EUROPE | $34.73M | $108.33M | **$143.06M** | **70%** |
| META | $3.85M | $4.73M | **$8.58M** | 4% |
| NA | $11.42M | −$0.63M | **$10.79M** | 5% |
| LA | $32.64M | $8.00M | **$40.65M** | 20% |
| **Total** | **$82.48M** | **$121.63M** | **$204.11M** | 100% |

- $/CA：$25.18（全量）、$17.30（Standard PN）、$36.44（CPN）
- 完整数据口径：实际 PR 5.97% → 目标 PR 8.24%，增量 $204M
- **$204M 已逐行验证**（Calc Bookings = HW × Target PR，DP Benefit = Calc − SVC，按 geo×CPN 重算吻合）

---

## 三、口径问题澄清（今天的核心）

### 现象：两个都叫 "DP Benefit" 的表

| 表 | 结果 | 数据范围 |
|----|------|---------|
| DP Benefit (Premier) | **+$204M** | 完整 Raw Data（12 万行，HW $9.0B）|
| DP Benefit（"→ Min PR Benefit" 附近） | **−$13M** | 另一套数据（HW $3.56B）|

### 本质理解（三步流水账，待财务确认）

```
第 1 步  当前：ESS 定价逻辑（服务独立定价，有自己的价格规则）
         SVC Bkgs = $537.8M，ACT PR = 3.25%

第 2 步  口径转换：ESS → Pen Rate（不改 PR，只换算法）
         服务价 = 硬件价 × 渗透率，重新算一遍
         bookings 缩水（−$13M 那张表展示的即此步，方向对、数值是旧版）

第 3 步  提价：PR 拉到 Dell 目标（Target PR 8.24%）
         bookings 增加

净变化 = 提价收益 − 转换调整 = +$204M
```

**关键洞察**：ESS 的独立价格逻辑，算出的价格**高于** Pen Rate 口径在同等渗透率下的价格，所以换口径会让部分 revenue 缩水；$204M 是"转换损失被提价收益覆盖后的净额"。

### 反推结论

- **−$13M 的精确数字无法从当前 Raw Data 反推**：其数据源（HW $3.56B）不是完整数据（$9.0B）的任何子集（按 geo/product_tier/ess_premier/term/base_warranty 全维度验证过）；且 Raw Data 缺 "Cal PR" 字段（只有 Target PR）。
- 唯一弱线索：−$13M 表的 Cal PR（1.6%–6.7%）与 `DT PR Adjustment` 的 "Premier Pen Rate"（1.3%–7.3%）同量级，EUROPE/META 两 Geo 接近，暗示 Cal PR 可能是"Pen Rate 口径下的当前 PR"。但不能定论。

---

## 四、关键洞察

1. **EUROPE 是命门（70%）**：$204M 里 EUROPE 独占 $143M，其中 CPN $108M 是单点最大变量。整个 case 高度依赖 EUROPE 的 PR 提升空间兑现。
2. **AP 被实质放弃（0.5%）**：因联想 BM 地位，Dell 目标不适用、反而伤 bookings，被压到接近 0。这是"方法论在 AP 失效"的信号，AP 用什么替代逻辑需要交代。
3. **完整数据里也有负 benefit 组合**：NA 的 CPN（−$0.63M）、AP 的 Standard PN（−$0.17M），说明这些领域当前 PR 已超过 Dell 目标，"对标提价"没有空间。
4. **未纳入项全部指向高估**：HW Cannibalization、高 ASP 降 attach、低 ASP 升 attach 三个弹性项都没算，$204M 应视为上限。

---

## 五、待确认（已发邮件问财务）

邮件问的是三个**本质问题**（不涉数据细节）：

1. 从 ESS 切到 Pen Rate（不改 rate）本身，revenue 是升、降还是不变？是真实价格变化还是记账差异？
2. $204M 是不是净额（提价收益 − 转换调整）？
3. ESS 逻辑下，是否有服务定价**高于** Pen Rate 在同等 rate 下的价格？（即转换会"吐回"的那部分）

---

## 六、我的评估

**Case 逻辑自洽，但 $204M 偏乐观，且口径命名有硬伤。**

- 可用的：方法论清晰（PR 对标 → 重算 bookings → 增量），Premier 数据充分，DT/WS 分层、Japan/Brazil 标准化到位。
- 要压的：EUROPE 单点依赖（70%）、AP 方法论真空、HW AUR 乘数、三个未纳入弹性项。
- 命名硬伤：两个表都叫 "DP Benefit"，评审必问"信哪个"；−$13M 那张（Cal PR 口径）应删掉或明确标为"口径转换调整"。
- 下一步：等财务回复后，重算"转换调整量"，把 $204M 拆成"提价真收益 − 转换损失"的准确流水账。
