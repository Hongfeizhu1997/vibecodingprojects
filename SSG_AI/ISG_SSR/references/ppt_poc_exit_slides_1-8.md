# Easy Service Sale Smart Recommendation — POC Exit PPT (前8页内容)

> 来源: Easy Service Sale Smart Recommendation_POC Exit.pptx
> 提取日期: 2026-05-28
> 项目: SSG AI / ISG SSR

---

## Slide 1: 封面
Easy Service Sale Smart Recommendation

## Slide 2: 业务背景 — B2B Oppty to Contract Process

Lenovo GPS 在 B2B 场景中面临的核心挑战：
- 服务产品体系复杂：Hard Bundle (CLFO) / Soft Bundle / CTO Service / Standard PN / Solution ID
- 涉及角色多：ISO / SSG / DT/IT
- 场景多样：Scenario-service / Scenario-sales

核心痛点：
1. How to get a service recommendation I need?
2. How to ensure customer accept that?
3. How to guarantee the customer will buy that?
4. How to recommend a service that sales need?
5. How to ensure the recommendation align with SSG sales and product strategy?
6. How to support this controversial and complex scenario?

## Slide 3: 双维度 KPI

- Operational: *To be finalized with business stakeholders
- Financial: **Statistics based on 2025 FY data

## Slide 4: AI 推荐引擎 — 4 层思维模型

输入: Bid Creation → Customer DMU / Segment / Country / CTO / Vertical / Configuration / HW Value / Premier Asset Tag / CO2 Offset Label / ESS Selection / Auto Configuration Service

AI Recommendation Engine — 4-Layer Thinking:
1. Popularity Ranking
2. Product Association
3. Historical Data Based Machine Learning
4. Business Rule Filter

无历史数据场景特殊处理 (No Historical Data Available)

输出格式 (GBB 三档):
- Warranty + Term N (%)
- Add on N.1 (%), Add on N.2 (%), Add on N.3 (%)
- CO2 Offset N (%)

推荐理由: Historical Data + Pre-defined Statistics + LLM

GBB Display 逻辑:
- 无概率 > 75%: Warranty 1 (Default) / Warranty 2 / Warranty 3
- 有概率 > 75%: Warranty 1 (Default) / Warranty 1 + Add on 1 / Warranty 1 + Add on 1 + CO2 1

Reason Display:
- 有统计亮点 → prompt 基于亮点
- 无统计亮点 → prompt 通用

待定: SBB default logic (Need to close)

## Slide 5: 技术架构 — 四引擎

Data Pool (300+ Fields) → Feature Pool (50+ Points)

引擎架构:
- Engine I — Cold Start Engine: Association Rule Engine
- Engine II — Recommendation Engine: Popularity Ranking + Product Association (Service)
- Engine III — Business Adaptation Engine: Feature Embedding → Feature Extracting → Feature Scoring → Key-Value Adaptation → Large Language Model
- Engine IV: Topic Modeling, LLM + Recall & Ranking, Business Rules, Baseline Setting…

数据维度: Hardware / Service / Customer / Contract / Bid / Price

口号: 推的都队！(Right On Target!)
专利: Lenovo Patent IDF - 172585

## Slide 6: POC 验证计划

范围: EMEA (Denmark, France, Spain)
数据: 100K 条 (70K 训练, 30K 测试), 1年配置历史
退出标准: 准确率 > 50%
预期表现: 测试集准确率 > 61%

## Slide 7: GBB 分档逻辑 — 决策流程

AI Model 输出 N 个保修计划 (每个含顶层概率 + 嵌套 Add-on 模块)
约束: Σ 顶层概率 = 1, 每个多选项模块内 Σ 概率 = 1

系统检查: 任意计划概率 > 0.75?

Branch 1 (No): 按实际价格排序 → Good/Better/Best → 仅展示基础保修
Branch 2 (Yes): 选最高概率计划 → 逐模块取最高概率选项 → 按概率降序排列 → 三档叠加

## Slide 8: 具体示例

Branch 1 示例 (max prob = 0.40):
  Good:  Plan A 3Y Pre NBD
  Better: Plan C 4Y Basic
  Best:   Plan B 5Y Pre NBD

Branch 2 示例 (Plan B prob = 0.85):
  模块排序: CO₂ Offset (0.9) > Biz Hours Install (0.9) > KYD (0.7) > CRS 5Y-6hr (0.7)
  Good:   5Y Pre NBD
  Better: + CO₂ Offset
  Best:   + CO₂ Offset + Biz Hours Install
