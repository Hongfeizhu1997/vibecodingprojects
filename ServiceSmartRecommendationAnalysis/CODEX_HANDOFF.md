# Codex Handoff: Service Smart Recommendation (SSR) Analysis Project

> **目标**：让另一台电脑上的 Codex 完全理解此项目的背景、方法论、数据结构和当前状态。
> **最后更新**：2026-06-25

---

## 一、项目是什么

**Service Smart Recommendation (SSR)** 是联想 ISG（Infrastructure Solutions Group）的一个 AI 推荐引擎项目。在硬件配置阶段，AI 推荐合适的服务产品（保修/支持合同），卖家可以选择接受、替换或跳过。

本项目的工作是对 SSR 的**业务效果进行量化分析**，回答「这项目到底带来了多少收入」。

---

## 二、项目包含两个子项目

### 子项目 A：事后 KPI 分析（已基本完成）

**目录**：`ServiceSmartRecommendationAnalysis/`（本目录）
**定位**：用真实交易数据验证 SSR 的业务效果
**包含 3 个 Phase**：

| Phase | 关注点 | 核心方法 | 关键产出 |
|-------|--------|---------|---------|
| **Phase 1** | 操作层 KPI | Coverage / Acceptance / Attach Rate × GEO × CTO类型 | `validation_output/phase1_operational_kpi_report_v2.html` |
| **Phase 2 V1** | 财务 KPI（保守） | DiD + 收入分解，扣除有机增长 | $13.6M 归因；报告 `phase2_financial_kpi_report_v1.html` |
| **Phase 2 V2** | 财务 KPI（乐观） | 恒定服务价格框架（老板 guidance） | $28.3M 归因；报告 `phase2_financial_kpi_report_v2.html` |
| **Phase 3 V1** | 整合验证（保守框架） | 操作↔财务交叉验证 | 报告 `phase3_integrated_report_v1.html` |
| **Phase 3 V2** | 整合验证（乐观框架） | 桥接分析 + 年度投影 $40-56M | 报告 `phase3_integrated_report_v2.html` |

**结论**：真实 SSR 贡献在 $14-28M 之间（V1 下界 / V2 上界）。NA 是冷启动 GEO，需要防御性归因。

### 子项目 B：前瞻方案探索（进行中）

**目录**：`SSG_AI/ISG_SSR/`（SSG AI 母舰下）
**定位**：SSR 未来版本的架构设计
**核心内容**：

- `analysis/insights/llm_explanation_generation.md` — LLM 生成推荐理由的完整方案（Stage 7）
- `analysis/insights/api_schema_model_catalog_contract.md` — Model → Catalog JSON Schema
- `analysis/insights/feature_business_language_mapping.md` — 30+ 特征的双版映射表
- `analysis/insights/skill-packaging-feasibility.md` — 将 SSR 打包为可复用 Skill 的可行性分析
- `analysis/models/recommendation_model_overview.md` — XGBoost 推荐模型技术参考
- `outputs/diagrams/isg-ssr-full-story.html` — 全故事动画演示（17 stage）

---

## 三、数据源

### 操作层数据（配置阶段）
| 文件 | 大小 | 内容 |
|------|------|------|
| `Ai_Report_20250815~20260306.xlsx` | 68MB | 268K 行配置交易记录，38 列 |
| `Ai_Report_2026-04-01(3.17-4.01).xlsx` | 8.6MB | 补充数据（Mar 17–Apr 1） |

关键列：`refId`, `configuredFrom` (New CTO/Copied CTO/MTM), `geo`, `country`, `defaultFrom` (AI/Non-AI), `defaultServicePn1`, `selectedFrom`, `selectedServicePn1`, `createdDate`

### 财务层数据（订单阶段）
| 文件 | 大小 | 内容 |
|------|------|------|
| `ESS Smart Recommendation Performance_Q4 analysis.xlsx` | 6.1MB | Q4 FY25/26 订单，Sheet1=70K行明细 |
| `ESS Smart Recommendation Performance_Q3 analysis.xlsx` | 7.0MB | Q3 FY25/26 订单 |

关键列：`quarter`, `scenario_flag`, `Sum(svcs_bookings)`, `Sum(total_bookings)`, `Sum(hw_qty)`, `geo`, `$/HW`, `penetration_rate`

Sheet3 是预聚合的 GEO × Quarter 汇总表，**分析通常从 Sheet3 开始**。

### 关键定义
- **联想财年**：Q1=Apr–Jun, Q2=Jul–Sep, Q3=Oct–Dec, Q4=Jan–Mar
- **EMEA 部署时间线**：Pilot Aug 15 (Q2) → Full Sep 28 (Q3)
- **WW 部署**：Nov 28 (Q3)
- **合同到收入确认延迟**：1-2 个月（→ NA/AP/LA 的 Q3 收入实际不受项目影响，这是 DiD 的关键）

---

## 四、核心方法论（Codex 必须理解）

### 4.1 操作层 KPI（Phase 1）

| 指标 | 公式 | 含义 |
|------|------|------|
| Coverage | 有推荐默认值 ÷ 总配置数 | 系统覆盖范围 |
| Acceptance Rate | 卖家保留默认推荐 ÷ 有默认的配置 | 卖家信任度 |
| Attach Rate | 选了服务 ÷ 总配置数 | 最终服务附加率 |
| Attachment Failure | 有推荐但没选任何服务 ÷ 有推荐的配置 | AI 存在但未转化 |

**关键分层**：
- **New CTO vs Copied CTO**：New CTO 接受率通常低 30-42pp（因为卖家不熟悉配置），是最大改善杠杆
- **AI vs Non-AI 默认来源**：AI 来源接受率 26-34%，Non-AI（规则/legacy）70-85%
- **国家钻取**：Brazil (BR), Thailand (TH), Turkey (TR) 通常是异常低接受率

### 4.2 Phase 2 V1：DiD + 收入分解（保守框架）

**核心**：不是所有 $/HW 增长都来自项目，必须剥离有机增长。

```
DiD = (Treatment_post - Treatment_pre) - (Control_post - Control_pre)
Project Revenue = DiD × Treatment HW Qty
```

**关键假设和验证**：
- Lenovo 有机增长率 = 14.4%（IDC Q4 YoY 出货增长）
- **不要假设固定 75% ASP 传导率**——实测传导比在 -3.9x ~ +10x 之间剧烈波动，固定假设不成立
- W10 EOS 在 Q3 贡献额外 +5pp YoY 增长（峰值），Q4 尾部 +3pp
- **DiD 之后不要再叠加主观归因率**——双重扣除

**结果**：
- EMEA Q3: $9.0M (DiD)
- EMEA Q4: $3.7M (分解)
- AP Q4: $2.0M
- LA Q4: $0.1M
- NA Q4: -$1.2M（冷启动，但绝对值 #1）
- **合计：$13.6M**

### 4.3 Phase 2 V2：恒定服务价格框架（老板 guidance）

**核心**：假设服务产品价格 YoY 不变 → $/HW 的任何增长 = 项目贡献。

```
项目贡献 = $/HW 增长率 × 服务收入（仅当增长 > 0）
```

**结果**：$28.3M（EMEA Q3 $11.6M + Q4 $11.7M + AP Q4 $4.9M + LA Q4 $0.1M；NA Q4 -1.6% → $0）

**V1 vs V2**：V1 是下界估计（扣除有机），V2 是上界估计（全部归因），真相在 $14-28M。

### 4.4 Phase 3：整合验证

**核心逻辑**：操作 KPI ↑ 应该可以解释财务 KPI ↑。
- 相关性实测：+0.87，确认操作改善传导到财务
- 接受率-ACV 悖论：Q2→Q4 接受率从 55%+ 微降至 ~50%，但 ACV 从 $655→$822 → 引擎从"体积附着"转向"价值附着"
- Mix Effect 优先排查：整体接受率下降时，先拆 New CTO vs Copied CTO。EMEA 整体 -3.2pp，但 New CTO 实际 +5.8pp——下降全部来自 New CTO 占比从 54.5%→64.6% 的 mix shift

### 4.5 NA 冷启动诊断（重要）

NA Q4 $/HW 增长 -1.6%，但不要直接判定为项目失败。运行 4 步诊断：

1. **检查项目前有机趋势**：NA FY24 $/HW 从 $36.38→$51.90（+42.6%），W10 EOS 驱动的不可持续峰值
2. **检查分母稀释**：NA Q4 HW Qty +27.8% QoQ → $/HW 机械性下降
3. **检查 HW ASP**：NA ASP 仅 +0.4%（vs EMEA +15%），完全没有保护色
4. **对比绝对值**：NA $/HW $51.07（#1），ACV $89,082（#1）——"负增长"是统计学假象

**结论**：NA 的贡献是**防御性**的——在 W10 EOS 消退时保住了服务附加率。估算防御价值 $3-6M。

---

## 五、文件结构

```
ServiceSmartRecommendationAnalysis/
├── background.txt                          ← 原始任务描述（验证 SSR 效果分析）
├── CODEX_HANDOFF.md                        ← 本文件
├── phase1_analysis.py                      ← Phase 1 主分析脚本
├── build_report.py / build_report_v2.py    ← 报告生成脚本
├── analyze_term_type.py / analyze_term_type_all.py  ← Term×Type 分析
├── analysis_acceptance.py                  ← 接受率专项分析
├── load_historical.py                      ← 历史数据加载
├── explore_*.py                            ← 数据探索脚本
├── validate.py                             ← 验证脚本
└── validation_output/
    ├── phase1_operational_kpi_report_v2.html   ← Phase 1 最新报告
    ├── phase2_financial_kpi_report_v1.html     ← DiD 框架财务报告
    ├── phase2_financial_kpi_report_v2.html     ← 恒定价格框架财务报告
    ├── phase3_integrated_report_v1.html        ← 整合验证 V1
    ├── phase3_integrated_report_v2.html        ← 整合验证 V2
    └── na_underperformance_diagnosis.html      ← NA 专项诊断

SSG_AI/ISG_SSR/
├── README.md                               ← ISG SSR 子项目总览
├── analysis/
│   ├── models/recommendation_model_overview.md
│   └── insights/
│       ├── llm_explanation_generation.md
│       ├── api_schema_model_catalog_contract.md
│       ├── feature_business_language_mapping.md
│       ├── model_explainability.md
│       └── skill-packaging-feasibility.md
├── outputs/diagrams/                       ← 7 个 HTML 架构图/动画
└── notes/progress.md
```

---

## 六、关键陷阱（Codex 必须避免）

1. **不要盲目信任已有分析**。每个假设都要对数据验证——特别是主观归因率、75% ASP 传导、有机增长基线
2. **先建 FY24 基线再判趋势**。不建基准就断言"增长"或"下降"会得出错误结论
3. **接受率下降不一定是坏事**。先排查 Mix Effect——整体接受率下降可能是 New CTO 占比上升导致的假象
4. **NA 负增长不是项目失败**。绝对值 #1 但增长率为负 = 基线异常高的统计学假象
5. **DiD 不要再叠加归因率**。双重扣除
6. **ASP 传导假设不成立时必须放弃**。实测值跨季度剧烈波动，不能用固定数字
7. **Coverage 接近天花板后，杠杆转向 accept quality**：97%+ 覆盖率下，21% attach failure 是下一个突破口
8. **不要假设列名含义**。`defaultFrom` 在不同数据源可能有不同语义，先验证

---

## 七、已知关键基准数据

### EMEA 操作指标（FY24 → FY25/26）
| 指标 | FY24 | FY25/26 | Δ |
|------|------|---------|---|
| Coverage | 74.4% | 94.4% | +20pp |
| Acceptance | 37.5% | 54.4% | +17pp |
| Attach | 53.1% | 73.6% | +21pp |

### $/HW 关键值（Q3 FY25/26 vs Q3 FY24/25）
| GEO | 基准（去年） | 当前 | Δ |
|-----|-----------|------|-----|
| EMEA | $41.51 | $46.83 | +12.8% |
| NA | $38.37 | $51.07 | +33.1%（但无项目暴露） |
| AP | $30.60 | $37.36 | +22.1% |
| LA | $22.59 | $24.80 | +9.8% |

---

## 八、Codex 启动后的建议步骤

1. **先读** `background.txt` 理解原始任务
2. **读 Phase 1-3 的 HTML 报告**，理解已有分析框架和结论
3. **检查数据文件**是否存在（4 个 xlsx 文件）
4. **如果数据文件缺失**：先确认能拿到数据再跑分析；不要在没有数据的情况下猜测
5. **如果有新一批数据**：复用 `phase1_analysis.py` / `build_report.py` 的框架，更新数据源路径即可
6. **如果收到新的分析问题**：先理解问题 → 对照已有方法论 → 确认是否需要新方法 → 再动手

联系人（项目背景问题）：hongfeizhu
