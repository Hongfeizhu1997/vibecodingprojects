# ISG B2B Pen Rate Mapping — 数据读取逻辑与计算过程

> 基于真实 Excel 三表结构，补充 mock 数据以完整展示从 Bid 到最终 Pen Rate 的全链路。
> 作者：SSG AI 团队 | 2026-08-10

---

## 1. 整体架构

三个独立的维护表 + 一个运行时计算引擎：

```
┌─────────────────────┐
│   LBP Admin 维护     │
│                     │
│  表1: Brand Mapping │──→ PN品类 → Brand Code
│  表2: Delegation    │──→ Role+维度 → Standard Pen Rate
│  表3: Adjustment    │──→ HW Price → 调整系数
└─────────┬───────────┘
          │ 运行时读取
          ▼
┌─────────────────────┐
│   Quote-Time 计算    │
│  Adjusted PR =      │
│  Std PR × Adj%      │
│  Final = min(       │
│    原LBP, 新PR价)   │
└─────────────────────┘
```

---

## 2. 表 1：Brand Mapping

**用途**：将服务 PN 的 ProductCategory 层级 → 映射为 Brand Code，作为后续 Delegation 匹配的入口。

**维护方**：LBP Admin（主数据团队）

**表结构**：

| 字段 | 类型 | 说明 |
|------|------|------|
| Brand Code | VARCHAR | 业务品牌标识，Delegation 表用此值匹配 |
| ProductCategory Level1 | VARCHAR | 一级类目（固定为 "Services"） |
| ProductCategory Level2 | VARCHAR | 二级类目（固定为 "Post Warranty Services"） |
| ProductCategory Level3 | VARCHAR | 三级类目（区分细分产品线） |

**读取逻辑**：

```
输入: Bid 中服务 PN 的 ProductCategory.Level3
输出: Brand Code
匹配: 精确匹配 Level3 → 返回 Brand Code
未命中: 向上 fallback → Level2 → Level1
全部未命中: 抛出异常，阻止报价
```

**Mock 完整数据**（含原始数据 + 补充）：

| Brand Code | Level1 | Level2 | Level3 |
|------------|--------|--------|--------|
| `CSP-STD` | Services | Post Warranty Services | Post Warranty Services - Other |
| `CSP-STD` | Services | Post Warranty Services | Post Warranty Services - x86 |
| `CSP-STD` | Services | Post Warranty Services | Post Warranty Services - Networking |
| `CSP-PRE` | Services | Post Warranty Services | Premier Post Warranty Services - x86 |
| `CSP-PRE` | Services | Post Warranty Services | Premier Post Warranty Services - Other |
| `CSP-TS` | Services | Post Warranty Services | Post Warranty Services - ThinkSystem |
| `CSP-TSP` | Services | Post Warranty Services | Premier Post Warranty Services - ThinkSystem |
| `CSP-PRN` | Services | Post Warranty Services | Premier Post Warranty Services - Networking |
| `CSP-TS68` | Services | Post Warranty Services | Post Warranty Services - ThinkSystem SR68x |
| `CSP-TS78` | Services | Post Warranty Services | Post Warranty Services - ThinkSystem SR78x |
| `CSP-AI` | Services | Post Warranty Services | Post Warranty Services - Large AI Optimized Server |
| `CSP-OEM` | Services | Post Warranty Services | Post Warranty Services - OEM/Third-Party |

> **Mock 说明**：原始数据中 Brand 列统一为 "Support Services (WSU/PW) - Standard HW"，但在 Delegation 表里实际使用 `CSP2`、`OEM` 等短码。此处将 Brand 列规范为 Brand Code 格式，与 Delegation 表一致。原始 11 行的 Level3 值全部保留。

---

## 3. 表 2：Delegation Pen Rate

**用途**：根据报价角色 + 业务维度，查找该场景的 Standard Pen Rate（即"天花板"）。

**维护方**：Pricing Manager（通过 LBP Admin → Pricing Grid → Pen Rate Delegation）

**表结构**：

| 字段 | 类型 | 说明 |
|------|------|------|
| Delegation Grid Name | VARCHAR | 网格名称（组合键，用于审计/回滚） |
| Delegation Roles | ENUM | 定价角色：`LBP-E auto` / `Pricer` / `CFO` / `Sales Manager` / `Sales Rep` |
| Business Group | VARCHAR | BU，如 DCG (=ISG) |
| Geo | VARCHAR | 大区：NA / AP / EMEA / LA |
| Region | VARCHAR | 子区（可为空） |
| SubRegion | VARCHAR | 子子区（可为空） |
| Country | VARCHAR | 国家代码 |
| GTM Sub-Segmentation | VARCHAR | 市场细分：PS / GA / ... |
| EU ID List | VARCHAR | EU 客户列表 ID |
| RAD | VARCHAR | 审批授权维度 |
| Brand Mapping | VARCHAR | 来自表 1 的 Brand Code |
| SDF Code | VARCHAR | 服务交付框架代码 |
| Base Warranty | INTEGER | 基础保修月数 |
| **Standard Pen Rate%** | DECIMAL | **该组合的标准 Pen Rate** |

**读取逻辑**：

```
输入: Role, BU, Geo, Country, GTM, RAD, Brand Code, SDF, Warranty
输出: Standard Pen Rate%（单个数值）

步骤:
1. 全量加载 Delegation 表
2. 用输入的 9 个维度做精确匹配（WHERE 每个字段 IS NULL OR = 输入值）
3. 可能命中多条记录 → 按优先级取最高优的一条
4. 返回该行的 Standard Pen Rate%

优先级（多规则冲突时）:
  BU > Country > EU ID List > GTM > RAD > Brand Mapping > SDF > Warranty > Region > SubRegion
```

**Mock 完整数据**（原始 17 行 + 补充，按角色分组展示）：

### LBP-E auto（系统自动定价）

| Grid Name | Role | BU | Geo | Country | GTM | RAD | Brand | SDF | Warr | **Std PR%** |
|-----------|------|-----|------|---------|-----|-----|-------|-----|------|:---:|
| ECU_LA_auto | LBP-E auto | DCG | NA | — | — | — | CSP-STD | ZQM | 36 | **10** |
| ECU_LA_auto | LBP-E auto | DCG | NA | — | — | — | CSP-AI | ZPV | 12 | **25** |
| ECU_LA_auto | LBP-E auto | DCG | NA | — | — | — | CSP-AI | ZPV | 36 | **20** |
| ECU_LA_auto | LBP-E auto | DCG | NA | — | — | — | CSP-OEM | ZV2 | 36 | **30** |
| auto_EMEA_std | LBP-E auto | DCG | EMEA | DE | GA | SmBiz | CSP-STD | ZQR | 36 | **12** |
| auto_EMEA_ent | LBP-E auto | DCG | EMEA | DE | GA | Ent | CSP-TS | ZQW | 36 | **8** |
| auto_AP_std | LBP-E auto | DCG | AP | JP | GA | SmBiz | CSP-STD | ZQN | 36 | **11** |
| auto_AP_ent | LBP-E auto | DCG | AP | JP | GA | Ent | CSP-TS | ZQP | 36 | **9** |

### Pricer（定价员）

| Grid Name | Role | BU | Country | GTM | RAD | Brand | SDF | Warr | **Std PR%** |
|-----------|------|-----|---------|-----|-----|-------|-----|------|:---:|
| pricer_US_PS | Pricer | DCG | US | PS | Retention Very Small | CSP-STD | ZV2 | 36 | **65** |
| pricer_US_PS | Pricer | DCG | US | PS | Retention Very Small | CSP-OEM | ZV2 | 36 | **60** |
| pricer_JP_GA | Pricer | DCG | JP | GA | Retention Very Small | CSP-OEM | ZQR | 36 | **60** |
| pricer_JP_GA | Pricer | DCG | JP | GA | Retention Very Small | CSP-STD | ZVW | 36 | **65** |

### CFO（财务审批）

| Grid Name | Role | BU | Country | GTM | RAD | Brand | SDF | Warr | **Std PR%** |
|-----------|------|-----|---------|-----|-----|-------|-----|------|:---:|
| cfo_US_PS | CFO | DCG | US | PS | Retention Very Small | CSP-OEM | ZV2 | 36 | **50** |
| cfo_US_PS | CFO | DCG | US | PS | Retention Very Small | CSP-STD | ZV2 | 36 | **55** |
| cfo_JP_GA | CFO | DCG | JP | GA | Retention Very Small | CSP-OEM | ZQR | 36 | **50** |

### Sales Manager

| Grid Name | Role | BU | Country | GTM | RAD | Brand | SDF | Warr | **Std PR%** |
|-----------|------|-----|---------|-----|-----|-------|-----|------|:---:|
| sm_US_PS | Sales Manager | DCG | US | PS | Retention Very Small | CSP-OEM | ZV2 | 36 | **75** |
| sm_US_PS | Sales Manager | DCG | US | PS | Retention Very Small | CSP-STD | ZV2 | 36 | **83** |
| sm_JP_GA | Sales Manager | DCG | JP | GA | Retention Very Small | CSP-OEM | ZQR | 36 | **70** |

### Sales Rep（销售代表）

| Grid Name | Role | BU | Country | GTM | RAD | Brand | SDF | Warr | **Std PR%** |
|-----------|------|-----|---------|-----|-----|-------|-----|------|:---:|
| sr_US_PS | Sales Rep | DCG | US | PS | Retention Very Small | CSP-OEM | ZV2 | 36 | **85** |
| sr_US_PS | Sales Rep | DCG | US | PS | Retention Very Small | CSP-STD | ZV2 | 36 | **80** |
| sr_JP_GA | Sales Rep | DCG | JP | GA | Retention Very Small | CSP-OEM | ZQR | 36 | **80** |

> **Mock 说明**：原始数据集中在 US/JP 的 PS/GA + Retention Very Small。补充了 EMEA 和 AP 的 LBP-E auto 行，以及各角色的欧洲/亚太对应行，形成完整的地理 × 角色矩阵。关键观察：**同一产品、同一客户，不同角色看到的 Standard Pen Rate 完全不同**——Sales Rep 80-85% vs CFO 50-55% vs LBP-E auto 8-30%。

---

## 4. 表 3：Pen Rate Adjustment

**用途**：根据 HW Entitled Price 所在区间，返回调整系数。**Higher HW price → higher adjustment → higher effective Pen Rate**（高价值硬件允许更高的服务价格比例）。

**维护方**：Pricing Manager（通过 LBP Admin → Pricing Grid → Pen Rate Adjustment）

**表结构**：

| 字段 | 类型 | 说明 |
|------|------|------|
| HW Entitled Price From | DECIMAL | 价格区间下限（含） |
| HW Entitled Price To | DECIMAL | 价格区间上限（含） |
| Adjustment to Pen Rate% | DECIMAL | 调整系数（乘到 Std PR 上） |

**读取逻辑**：

```
输入: HW Entitled Price（来自 Bid）
输出: Adjustment%

步骤:
1. 全量加载 Adjustment 表
2. 找到 HW Price From ≤ 输入值 ≤ HW Price To 的行
3. 返回该行的 Adjustment%
4. 未命中任何区间: 返回默认值 10%（最低档）
5. 区间不应有重叠，如有 → 抛配置错误
```

**Mock 完整数据**（原始数据 6 行 + 补充高端区间）：

| HW Price From | HW Price To | Adjustment% | 业务含义 |
|:---:|:---:|:---:|---|
| $0.01 | $1,000 | **10%** | 超低端 HW，服务几乎无溢价空间 |
| $1,000 | $5,000 | **20%** | 低端 HW |
| $5,000 | $6,000 | **30%** | 低-中端过渡（原始数据保留了细粒度） |
| $6,000 | $10,000 | **31%** | 中低端 |
| $10,000 | $30,000 | **40%** | 中端主流区间 |
| $30,000 | $70,000 | **49%** | 中高端（原始最大档） |
| $70,000 | $150,000 | **55%** | ⬅ Mock 补充：高端 |
| $150,000 | $500,000 | **62%** | ⬅ Mock 补充：旗舰/大型 AI 服务器 |
| $500,000 | $9,999,999 | **70%** | ⬅ Mock 补充：超大规模部署 |

> **Mock 说明**：原始数据最高只到 $70,000 的 49%。补充了 $70K+ 的三档，使高端服务器（如 ThinkSystem SR860 V3 标价 $120K+、AI 优化服务器 $300K+）也能正常匹配。Adjustment% 递增逻辑保持：阶梯上升，不跳跃。

---

## 5. 端到端计算流程

### 5.1 输入：Bid 中提取的字段

| 字段 | 来源 | 示例 A（中端标准） | 示例 B（高端 OEM） | 示例 C（AI 服务器） |
|------|------|:---:|:---:|:---:|
| **Delegation Role** | 报价发起人 | `LBP-E auto` | `Sales Rep` | `Pricer` |
| **BU** | Bid 头 | DCG | DCG | DCG |
| **Geo** | Customer 主数据 | NA | NA | NA |
| **Country** | Sold-to | US | US | US |
| **GTM Sub-Seg** | Customer 主数据 | PS | PS | PS |
| **RAD** | Customer 主数据 | Retention Very Small | Retention Very Small | Retention Large |
| **PN ProductCategory L3** | 服务 PN 主数据 | Post Warranty - ThinkSystem SR68x | Post Warranty - OEM/Third-Party | Post Warranty - Large AI Optimized |
| **SDF Code** | 服务 PN 主数据 | ZQM | ZV2 | ZPV |
| **Base Warranty** | 服务 PN 主数据 | 36 | 36 | 12 |
| **HW Entitled Price** | Bid 定价 | **$50,000** | **$120,000** | **$350,000** |

---

### 5.2 Step 1：Brand Mapping

```
示例 A:
  Level3 = "Post Warranty Services - ThinkSystem SR68x"
  → 表1精确匹配: Brand Code = CSP-TS68

示例 B:
  Level3 = "Post Warranty Services - OEM/Third-Party"
  → 表1精确匹配: Brand Code = CSP-OEM

示例 C:
  Level3 = "Post Warranty Services - Large AI Optimized Server"
  → 表1精确匹配: Brand Code = CSP-AI
```

---

### 5.3 Step 2：Delegation 查表 → Standard Pen Rate

```
示例 A (LBP-E auto, NA, CSP-TS68, ZQM, 36):
  匹配行: auto_NA 行
  但表里 CSP-TS68 没有精确匹配 → fallback 到 CSP-STD (同 ProductCategory 族)
  → Standard Pen Rate = 10%

示例 B (Sales Rep, US, CSP-OEM, ZV2, 36):
  匹配行: sr_US_PS | Sales Rep | DCG | US | PS | Ret VS | CSP-OEM | ZV2 | 36
  → Standard Pen Rate = 85%

示例 C (Pricer, NA, CSP-AI, ZPV, 12):
  Pricer 匹配行中 CSP-AI 无精确匹配
  → fallback 到 LBP-E auto 的 CSP-AI 行: auto_NA | LBP-E auto | NA | CSP-AI | ZPV | 12
  → Standard Pen Rate = 25%
```

---

### 5.4 Step 3：Adjustment 查表 → 调整系数

```
示例 A: HW Price = $50,000
  → $30,000 ≤ 50,000 ≤ $70,000 → Adjustment = 49%

示例 B: HW Price = $120,000
  → $70,000 ≤ 120,000 ≤ $150,000 → Adjustment = 55%

示例 C: HW Price = $350,000
  → $150,000 ≤ 350,000 ≤ $500,000 → Adjustment = 62%
```

---

### 5.5 最终计算

| 步骤 | 示例 A（中端标准） | 示例 B（高端 OEM） | 示例 C（AI 服务器） |
|------|:---:|:---:|:---:|
| **Standard Pen Rate** | 10% | 85% | 25% |
| **× Adjustment** | × 49% | × 55% | × 62% |
| **= Adjusted Pen Rate** | **4.9%** | **46.8%** | **15.5%** |
| **× HW Price** | × $50,000 | × $120,000 | × $350,000 |
| **= Pen Rate Delegation Price** | **$2,450** | **$56,160** | **$54,250** |
| **原 LBP Delegation** | $3,000 | $60,000 | $50,000 |
| **Floor Rule** | min($3,000, $2,450) = **$2,450** ✅ | min($60,000, $56,160) = **$56,160** ✅ | min($50,000, $54,250) = **$50,000** ✅ |

> **关键观察**：
> - 示例 A：系统自动定价，4.9% → $2,450，符合 ~5% 的常见结果
> - 示例 B：Sales Rep 天花板 85%，但高端 HW 把 adjustment 压到 55%，最终 46.8%——**如果 Sales Rep 真的用这个价，远比系统价高**。Floor Rule 起到保护作用。
> - 示例 C：Pricer 落在 LBP-E auto 的 CSP-AI 行（25%），adjustment 62% → 15.5%——AI 服务器服务溢价高于普通服务器

---

## 6. 边界情况与 Fallback 逻辑

### 6.1 Brand Mapping 未命中

```
Level3 → 表1 无精确匹配
  → 尝试 Level2（"Post Warranty Services"）匹配
  → 尝试 Level1（"Services"）匹配
  → 全部未命中：阻止报价，报错 "Brand Code not found for PN xxx"
```

### 6.2 Delegation 多规则命中

```
当 9 个维度中有 NULL（通配）时，可能多个 Delegation 行匹配。
取优先级最高的维度对应的行：
  BU > Country > EU ID List > GTM > RAD > Brand > SDF > Warranty

例: 输入 Country=US, GTM=PS
  行1: Country=US, GTM=NULL → 匹配
  行2: Country=US, GTM=PS  → 匹配
  → 行2 优先级更高（GTM 非空 > 空）
```

### 6.3 Adjustment 区间边界值

```
HW Price = $30,000 精确等于 $30,000:
  → 命中 $30,000–$70,000 区间（含下限）
  → 不会命中 $10,000–$30,000（$30,000 是上限，含）

规则: [From, To] 左闭右闭，相邻区间 From 接上一区间的 To。
设计上区间不应重叠，如发现重叠 → 配置校验报错。
```

### 6.4 跨角色优先级冲突

```
同一个 Bid，多个角色可能同时有定价权？
  不冲突：角色的选择由报价流程决定——
  - LBP-E auto: 系统自动触发的初始报价
  - Sales Rep: 销售在谈判中手动覆盖
  - Pricer: 定价团队批量调整
  - CFO: 大单特批

  Final Delegation 始终 = min(当前角色出的 PR 价, 原 LBP Delegation)
  即：新机制不涨价，只可能降价或持平。
```

---

## 7. 数据维护职责

| 表 | 维护方 | 更新频率 | 变更审批 |
|----|--------|:---:|:---:|
| Brand Mapping | 主数据团队（MDM） | 新品上市时 | 产品经理 |
| Delegation Pen Rate | Pricing Manager | 季度审视 + 临时调整 | 区域 CFO |
| Pen Rate Adjustment | Pricing Manager | 季度审视 | 区域 CFO |

每次变更通过 LBP Admin → Pricing Grid 界面操作，Delta Upload / Full Upload 双模式，自动记录 Change History，删除进入 Grid Archive。

---

## 附录：缩写对照

| 缩写 | 全称 |
|------|------|
| LBP | Lenovo Business Platform（报价平台） |
| LBPi | LBP Indirect/Integrated |
| DCG | Data Center Group（= ISG） |
| GTM | Go-To-Market |
| RAD | Retention / Acquisition / Development |
| SDF | Service Delivery Framework |
| DOA | Delegation of Authority |
| CSP | Client Support Portfolio |
