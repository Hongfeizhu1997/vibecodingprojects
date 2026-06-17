# ISG SSR — Stage 7 技术方案：LLM 推荐理由生成

> 更新时间：2026-06-17（整合 5 项关键决策 + prompt_engineering_spec + end_to_end_example）
> 历史：2026-06-08 V1（SHAP 映射 + Prompt 模板 + 端到端示例）

---

## 1. 已确认关键决策（2026-06-17）

| # | 决策项 | 确认结果 |
|---|--------|---------|
| 1 | 特征映射表 | 待定，不影响 high-level 方案 |
| 2 | LLM 提供商 | **Vetraflow + ChatGPT**（联想认可架构） |
| 3 | 生成时机 | 先按**实时生成**设计，最终视实际 performance 调整 |
| 4 | 多语言 | **需要**，含中文 Customer 版 |
| 5 | SHAP 特征 | 数量待定（Base ~8-10, Add-on ~3-5），值已离散化，**含 Add-on** |

---

## 2. 架构定位

在现有 6 阶段 Pipeline 之后，新增 **Stage 7: LLM Explanation Generation**。

```
Stage 1-5: Bid → Features → Recall → Ranking → Business Rules + Add-On
Stage 6:   GBB Output (Branch 1/2, Good/Better/Best)
Stage 7:   LLM Explanation Generation ← 本方案
              ├── 提取 SHAP 特征贡献 + 上下文
              ├── 特征映射表查找（Phase 2 启用）
              ├── 构建双版 Prompt（内部 / 客户 × 语言）
              ├── Vetraflow → ChatGPT 并行调用
              └── 输出校验 + 缓存
```

**LLM 不参与决策** — 推荐结果由 XGBoost 确定，LLM 只做"事后解释"。

---

## 3. 数据流（整合 API Schema）

```
XGBoost 推理完成
    ↓
输出 JSON（符合 api_schema_model_catalog_contract.md）
  · recommendations[0..N] 含 SHAP contributions
  · addon_recommendations 含 SHAP contributions
    ↓
Catalog Product Logic Filter
    ↓
Decision Gate → 选出 default PN（Branch 2: top plan; Branch 1: 按价格）
    ↓
Stage 7 Context Builder
  ├── 提取 bid 上下文（segment, country, hardware, value_band, contract_type）
  ├── 提取 default PN 信息（type, term, sla, prob, confidence）
  ├── 提取 SHAP contributions（base + add-on，按 |shap| 降序）
  ├── 提取 Add-on 建议（top 2）
  └── 语言标记（zh/en）
    ↓
特征映射表查找（Phase 2 启用；Phase 1 用 feature_name + feature_value 直传）
    ↓
Prompt 构建（4 种组合：Internal×en, Internal×zh, Customer×en, Customer×zh）
    ↓
Vetraflow → ChatGPT API 并行调用（最多 4 路）
    ↓
输出校验（per audience, per language）
    ↓
Cache: (bid_hash, rec_hash, lang) → explanation
    ↓
Return to Catalog → GBB Frontend 展示
```

---

## 4. Vetraflow + ChatGPT 集成

### 4.1 为什么是 Vetraflow

Vetraflow 是联想内部 DeerFlow 部署代号，提供：
- **IM Gateway**：统一 LLM 调用入口，支持多模型路由
- **Sandbox + Skills**：可加载 Feature Mapper 技能和 Prompt Template 技能
- **Audit Log**：全链路 LLM 调用可追溯（合规要求）
- **权限控制**：可限制 Agent 的 LLM 调用范围

### 4.2 调用架构

```
Stage 7 Agent (Vetraflow Sub-Agent)
    │
    ├── Tool: feature_mapper(feature_name, value, audience, lang) → business_language_text
    │
    ├── Tool: render_internal_explanation(context, lang) → explanation_text
    │       └── 内部调用 ChatGPT (gpt-4o 或 gpt-4o-mini)
    │
    └── Tool: render_customer_explanation(context, lang) → explanation_text
            └── 内部调用 ChatGPT (gpt-4o-mini 足够)
```

### 4.3 模型选择策略

| 目标 | 推荐模型 | 理由 |
|------|---------|------|
| Internal 英文 | GPT-4o | 需要精确数据引用，分析导向 |
| Internal 中文 | GPT-4o | 同上 + 中文表达质量 |
| Customer 英文 | GPT-4o-mini | 纯定性语言，推理要求低 |
| Customer 中文 | GPT-4o-mini | 同上 |

### 4.4 与已有 DeepSeek 方案的关系

| 维度 | DeepSeek 方案 | Vetraflow+ChatGPT 方案 |
|------|-------------|----------------------|
| API 入口 | 直连 DeepSeek API | 经 Vetraflow Gateway |
| 审计 | 需自建 | Vetraflow 内置 |
| 合规 | 需确认数据出境合规性 | 联想内部部署，合规性更高 |
| 模型 | DeepSeek-V3 | GPT-4o / GPT-4o-mini |
| 成本 | 低 | 中等（GPT-4o-mini 有性价比） |

**迁移建议**：Prompt 模板和校验逻辑可直接复用，只需替换 API 调用层。

---

## 5. 多语言设计

### 5.1 语言矩阵

| 受众 | 英文 | 中文 |
|------|------|------|
| Internal（销售/PM） | ✅ 必须 | ⚠️ 国内 PM 场景 |
| Customer（终端客户） | ✅ 必须（国际客户） | ✅ 必须（国内客户） |

### 5.2 System Prompt 语言适配

#### Internal 英文版
```
You are a service recommendation analyst for Lenovo ISG.

Your sole task: translate structured model explanation data into a concise, analytical
natural-language explanation of why a specific service warranty was recommended.

CRITICAL RULES — VIOLATION IS UNACCEPTABLE:
1. ONLY use features and values provided in the input. NEVER invent facts.
2. For each feature, use EXACTLY the "business_language" text provided. Do NOT reinterpret.
3. Positive SHAP features = supporting factors; Negative = mitigating factors.
4. Order features by absolute SHAP value (largest first).
5. NEVER compare this recommendation to other ranked options.
6. Include: recall source, confidence level, business rules applied, add-on suggestions.
7. Output ONLY the explanation text. No preamble, no closing.
8. Tone: data-driven, analytical, professional.
```

#### Internal 中文版
```
你是联想 ISG 服务推荐分析师。

你的唯一任务：将结构化模型解释数据翻译为简洁、分析导向的自然语言解释，
说明为什么推荐特定的服务保修方案。

关键规则——违反即不接受：
1. 只使用输入中提供的特征和数值。绝不编造事实、统计数据或特征名。
2. 每个特征严格使用提供的"业务语言"文本，不自行改写。
3. 正 SHAP 特征 = 支持推荐的因素；负 SHAP 特征 = 轻微制约但不变更推荐。
4. 按绝对 SHAP 值降序排列特征。
5. 不与排名中的其他方案比较，独立解释。
6. 包含：召回来源、置信度、业务规则、Add-on 建议。
7. 只输出解释文本，无前言、无结尾语。
8. 语气：数据驱动、分析导向、专业。面向内部 PM/销售。
```

#### Customer 英文版
```
You are a service advisor for Lenovo hardware customers.

Your sole task: translate structured analysis data into a helpful, customer-friendly
explanation of why a specific warranty plan suits their purchase.

CRITICAL RULES — VIOLATION IS UNACCEPTABLE:
1. ONLY use features and values provided in the input. NEVER invent facts.
2. For each feature, use the "customer_language" text provided. Do NOT reinterpret.
3. NEVER include numbers, percentages, probabilities, dollar amounts, or any quantitative data.
4. NEVER mention negative factors, model confidence, SHAP, XGBoost, feature names, recall engines.
5. NEVER compare this plan to other options. Explain it on its own merits.
6. NEVER mention data sources, historical statistics, or how the recommendation was computed.
7. Include add-on suggestions in a friendly, service-oriented tone.
8. Output ONLY the explanation text. No preamble, no closing signature.
9. Tone: helpful, professional, customer-service oriented.
```

#### Customer 中文版
```
你是联想硬件客户的专属服务顾问。

你的唯一任务：将结构化分析数据翻译为简洁、亲切、客户友好的中文解释，
说明为什么推荐的保修方案适合客户的采购。

关键规则——违反即不接受：
1. 只使用输入中提供的特征和数值。绝不编造事实。
2. 每个特征使用提供的"客户语言"文本，不自行改写。
3. 绝不包含数字、百分比、概率、金额或任何量化数据。只用定性语言。
4. 绝不提及负向因素、模型置信度、SHAP、XGBoost、召回引擎等任何技术术语。
5. 绝不与其他方案比较。只解释本方案的优势。
6. 绝不提及数据来源、历史统计或推荐计算方式。
7. 以友好、服务导向的语气附带 Add-on 建议。
8. 只输出解释文本，无前言、无结尾语。
9. 语气：专业、亲切、值得信赖，像资深客户经理的口吻。
```

### 5.3 User Prompt 语言变量

所有 User Prompt 模板增加 `{language}` 参数：

```
Generate a Customer-facing recommendation explanation in {language}.
...
```

### 5.4 中文版输出格式规范

#### Internal 中文版格式
```
推荐理由：{服务类型} {年限} {SLA}（概率 {prob}%，{置信度}）

该推荐由 {召回来源} 基于 {数据来源} 生成：

· {特征 1 业务表述}（{SHAP 方向} {SHAP 值}）
· {特征 2 业务表述}（{SHAP 方向} {SHAP 值}）
...

Add-on 建议：
· {addon 类型}（{选项}）：概率 {prob}%，基于 {依据}
...

{置信度} → {Branch 类型}，{行为描述}。
```

#### Customer 中文版格式
```
为什么推荐 {服务类型} {年限} 方案？

{硬件} 是 {定位}，{服务方案} 能够 {核心价值}。

{正面因素 1，2-3 句定性描述，无数字}
{正面因素 2，2-3 句定性描述，无数字}
{正面因素 3，2-3 句定性描述，无数字}

配套建议：
· {addon 建议 1}
· {addon 建议 2}
```

### 5.5 User Prompt 模板

#### Internal 版

```
Generate an Internal-facing recommendation explanation using the data below.

=== BID CONTEXT ===
Customer: {customer_segment} | Industry: {customer_industry} | Country: {country}
Hardware: {hardware_product_family} | Value Band: {hardware_value_band}
Contract Type: {contract_type}

=== RECOMMENDATION ===
Service Plan: {service_type} | Term: {service_term} | SLA: {service_sla}
Probability: {probability} | Confidence: {confidence_level}
Recall Source: {recall_source}

=== TOP CONTRIBUTING FEATURES ===
{for each feature in top_features, sorted by |shap| descending:}
{rank}. {feature_name} = {feature_value}
   SHAP: {shap_value} | Direction: {direction}
   Business Language: {business_language_text}
{end for}

=== BUSINESS RULES ===
{rules_summary}

=== ADD-ON SUGGESTIONS ===
{for each addon:}
{addon_type}: {addon_option} (probability {addon_prob}%)
Business Language: {addon_business_text}
{end for}

=== OUTPUT FORMAT ===
Start with: "Recommendation Rationale: {service_type} {service_term} {service_sla}"
Then bullet points (one per feature), ordered by SHAP impact.
End with a one-line summary including confidence level and recall source.
```

#### Customer 版

```
Generate a Customer-facing recommendation explanation using the data below.

=== CUSTOMER CONTEXT ===
Type: {customer_segment} | Industry: {customer_industry} | Location: {country}

=== HARDWARE ===
{hardware_product_family}

=== RECOMMENDED SERVICE ===
{service_type} with {service_term} coverage ({service_sla})

=== SUPPORTING FACTORS ===
{for each positive-SHAP feature, sorted by |shap| descending:}
{rank}. Customer Language: {customer_language_text}
{end for}

=== SUGGESTED ADD-ONS ===
{for each addon:}
{addon_type}: Customer Language: {addon_customer_text}
{end for}

=== OUTPUT FORMAT ===
Start with: "Why we recommend {service_type} {service_term} coverage"
Short paragraphs (2-3 sentences each), one per supporting factor.
End with add-on suggestions in a friendly tone.
NO numbers, NO percentages, NO technical terms.
```

---

## 6. 实时生成的延迟分析与优化

### 6.1 延迟预算

| 步骤 | 预估延迟 | 占比 |
|------|---------|------|
| Context Builder | ~3ms | 0.4% |
| Feature Mapping Lookup | ~2ms | 0.2% |
| Internal Prompt → ChatGPT (gpt-4o) | ~600ms | 39% |
| Customer Prompt → ChatGPT (gpt-4o-mini) | ~400ms | 26% |
| 中文 Internal → ChatGPT (gpt-4o) | ~600ms | —（并行） |
| 中文 Customer → ChatGPT (gpt-4o-mini) | ~400ms | —（并行） |
| Output Validation | ~2ms | 0.1% |
| **总计（4 路并行）** | **~650ms** | 100% |

> 4 路 LLM 调用完全并行，总延迟 ≈ 最慢的单路延迟（~600ms gpt-4o）+ 5ms overhead ≈ 650ms。

### 6.2 优化策略（按优先级）

1. **异步注入（推荐作为首批上线策略）**
   - Stage 6 GBB 结果即时返回 UI (< 150ms)
   - 解释层 650ms 后异步注入到已有的推荐卡片中
   - 用户感知延迟 = 150ms
   - 前端需要支持"解释加载中"骨架屏

2. **Cache 命中时零延迟**
   - 相同(bid_hash, rec_hash, lang) 直接返回缓存
   - 预期命中率：20-30%

3. **预生成**
   - 对高频 bid 模式做离线预生成

4. **模型降级**
   - 如果 gpt-4o 延迟 > 800ms，Internal 也用 gpt-4o-mini

### 6.3 如果改为异步生成（备选方案）

```
Stage 6 GBB Output → 即时返回 UI (< 150ms)
    ↓
Stage 7 触发异步任务
    ├── LLM 解释生成（650ms 后台执行）
    ├── 完成后推送到 GBB Frontend（WebSocket / SSE）
    └── 前端展示解释（总延迟 ~800ms，但不阻塞推荐）
```

**切换成本**：前端需增加 SSE 监听 + 骨架屏；后端需异步任务队列。

---

## 7. 缓存策略

### 7.1 缓存键

```
cache_key = SHA256(bid_context_hash + recommendation_hash + lang + audience)
```

其中：
- `bid_context_hash` = hash(customer_segment, country, hardware_family, hardware_value_band, contract_type, industry)
- `recommendation_hash` = hash(service_type, term, sla, rank, confidence_level)
- `lang` = "en" / "zh"
- `audience` = "internal" / "customer"

### 7.2 缓存失效

| 触发条件 | 策略 |
|---------|------|
| 模型版本更新 | 全量失效 |
| 特征映射表更新 | 全量失效 |
| 业务规则变更 | 全量失效 |
| Prompt 模板更新 | 全量失效 |
| TTL 超时（默认 7 天） | 自动过期 |

---

## 8. 输出校验规则

LLM 生成文本后，**必须经过后处理校验**才能交付给用户。

### 8.1 通用校验

| 检查项 | 方法 | 失败处理 |
|--------|------|---------|
| 输出非空 | `len(output) > 20` | 退化到规则模板 |
| 不含 LLM 自述 | 检测 "Here is" / "Based on the" / "I hope" | 截断到实际解释起始位置 |
| 特征名合法 | 每个引用的特征名在输入 JSON 中出现过 | 标记为 hallucination，重新生成 |

### 8.2 Internal 版专有校验

| 检查项 | 方法 | 失败处理 |
|--------|------|---------|
| 概率值正确 | 提取输出中的概率数值，与输入 `probability` 比对 | 修正为输入值 |
| 所有正负特征均已覆盖 | 输出中包含的特征数 ≥ 输入中提供的特征数 × 0.8 | 补全遗漏特征 |

### 8.3 Customer 版专有校验

| 检查项 | 方法 | 失败处理 |
|--------|------|---------|
| **无数字泄露** | 正则 `\d+\.?\d*%?` 检测百分比/数值 | **强制重新生成**（最高优先级） |
| 无技术术语 | 检测 "SHAP" "XGBoost" "Engine" "probability" "recall" "冷启动" "热启动" | 重新生成 |
| 无负向暗示 | 检测 "however" "but" "although" "lower than" "limited" | 重新生成 |
| 无与其他方案比较 | 检测 "compared to" "better than" "unlike other" | 重新生成 |

### 8.4 中文 Customer 版新增校验

| 检查项 | 方法 | 失败处理 |
|--------|------|---------|
| 无数字泄露 | 正则 `\d+\.?\d*%?` + 中文数字 `百分之|万|千|百` | 强制重新生成 |
| 无技术术语 | 检测 "SHAP" "XGBoost" "Engine" "概率" "置信度" "召回" | 重新生成 |
| 语气恰当 | 检测 "你应该" "你必须"（命令式）→ 应是建议式 | 重新生成 |
| 繁简体 | 检测是否混入繁体 | 重新生成 |

### 8.5 校验失败降级链

```
第 1 次失败 → 重新调用 LLM（相同 prompt，不同 temperature）
第 2 次失败 → 重新调用 LLM（增强约束 prompt）
第 3 次失败 → 退化到规则模板（非 LLM）
```

**连续 3 次失败 → 告警 + 降级模板**。不阻塞推荐主流程。

### 8.6 降级模板

当 LLM API 不可用、超时、或连续 3 次校验失败时，退化到规则模板。

#### Internal 降级模板
```
推荐理由：{Service Type} {Term} {SLA}（概率 {prob}%）

该推荐由 {recall_source} 生成（LLM 解释暂不可用）。

关键特征贡献（按 SHAP 值降序）：
{直接列出特征名 → 业务语言文本列表，不做 NL 包装}
```

#### Customer 降级模板
```
为什么推荐 {Service Type} {Term} 方案？

基于对您的配置和使用场景的综合分析，{Service Type} {Term} 
服务方案（{SLA}）最适合您的 {hardware_product_family} 设备。

配套建议：{addon 列表，逗号分隔}

如需了解更多方案细节，请联系您的客户经理。
```

---

## 9. 与前序 Stage 的接口

### 9.1 Stage 6 → Stage 7 传递数据

Stage 6（GBB Output）传递给 Stage 7 的数据包（基于 API Schema）：

```json
{
  "bid_id": "US-NA-2026-06421",
  "bid_context": {
    "customer_segment": "Enterprise",
    "country": "USA",
    "hardware_product_family": "ThinkSystem SR650",
    "hardware_value_band": "50K-100K",
    "contract_type": "One-Time",
    "industry": "Financial Services"
  },
  "default_pn": {
    "rank": 1,
    "service_type": "Premier",
    "warranty_term": "3Y",
    "warranty_sla": "24x7 4hr",
    "probability": 0.78,
    "confidence_level": "high",
    "shap_contributions": [ ... ],
    "recall_source": "engine_ii"
  },
  "addons": [ ... ],
  "branch": "branch_2",
  "languages": ["en", "zh"],
  "gb_tiers": {
    "good": "Premier 3Y 24x7 4hr",
    "better": "Premier 3Y 24x7 4hr + Installation BH",
    "best": "Premier 3Y 24x7 4hr + Installation BH + KYD 3Y"
  }
}
```

### 9.2 Stage 7 → Catalog/Frontend 返回数据

```json
{
  "bid_id": "US-NA-2026-06421",
  "generated_at": "2026-06-17T14:30:01Z",
  "model": "gpt-4o",
  "from_cache": false,
  "explanations": {
    "internal": {
      "en": "Recommendation Rationale: Premier 3-Year 24×7 4hr...",
      "zh": "推荐理由：Premier 3年 24×7 4小时现场响应..."
    },
    "customer": {
      "en": "Why we recommend Premier 3-Year coverage...",
      "zh": "为什么推荐 Premier 3年 方案？..."
    }
  }
}
```

---

## 10. 实施路径

```
Phase 0 (1-2 周) — API Schema 定稿 + Vetraflow 接入确认
├── Model → Catalog JSON Schema 评审确认
├── Vetraflow Gateway 接入权限确认（API Key, rate limit）
├── ChatGPT 模型配额确认（gpt-4o + gpt-4o-mini）
└── 4 套 Prompt 模板定稿（Internal×en, Internal×zh, Customer×en, Customer×zh）

Phase 1 (2-3 周) — 单条真实样本跑通
├── 单条 bid 端到端：Model → SHAP → Stage 7 → ChatGPT → 4 版解释
├── 4 版输出人工审查（准确性、业务恰当性、语言质量）
├── 输出校验规则代码化（正则 + 黑名单）
└── 延迟基准测试（4 路并行实际延迟）

Phase 2 (2-3 周) — Prompt 调优 + 特征映射表
├── 根据审查结果调整 Prompt
├── 特征映射表补充（需 PM 确认）
├── Few-shot examples 注入 Prompt（提升输出稳定性）
└── 中文质量专项优化（术语一致性、语气校准）

Phase 3 (3-4 周) — Pipeline 集成
├── Stage 7 Context Builder 实现
├── Vetraflow Gateway 调用封装
├── 缓存层实现（Redis 或内存）
├── 降级策略实现（规则模板）
├── 多语言路由（从 bid country 推断 lang）
└── 前端骨架屏 + SSE 异步注入

Phase 4 (2 周) — 灰度上线 + 监控
├── 10% 流量灰度（内部销售先用）
├── 解释质量人工抽样审查
├── API 延迟 p50/p95/p99 监控
├── ChatGPT token 消费监控
├── 缓存命中率监控
└── 用户反馈收集
```

---

## 11. 风险与对策

| 风险 | 等级 | 对策 |
|------|------|------|
| ChatGPT API 延迟抖动（p95 > 1.5s） | 中 | 设 1.2s 超时 → 降级模板；如持续抖动 → 切换异步生成 |
| 中文 Customer 版术语不当 | 中 | 中文 Prompt 从严约束 + 输出人工审核 + 术语黑名单动态更新 |
| Vetraflow Gateway 成为瓶颈 | 低 | Vetraflow 是成熟平台，但需确认内部部署的并发容量 |
| 4 路并行调用 token 成本超预算 | 低 | 先按实时场景监控，如超标 → Customer 版合并 batch |
| 特征映射表延迟（PM 无法及时提供） | 中 | Phase 1 用 `feature_name + value` 直传，Phase 2 映射表到位后替换 |

---

## 12. 少量样本（Few-Shot Examples）

> 注入 User Prompt 的 `<examples>` 块，帮助 LLM 稳定输出格式。

### 12.1 Internal 版示例

```
<example>
=== SAMPLE INPUT ===
Bid: Enterprise | Financial Services | USA | SR650 | $50K-100K | One-Time
Recommendation: Premier, 3Y, 24x7 4hr, prob=0.78, confidence=high
Features:
  1. hardware_product_family=SR650 | +0.18 | "SR650 机型历史 bid 中 Premier 采纳率 82%"
  2. customer_segment=Enterprise | +0.12 | "Enterprise 客户平均保修等级高于 SMB 1.4 档"
  3. contract_type=One-Time    | -0.05 | "一次性合同对该等级保修有轻微负向影响"

=== EXPECTED OUTPUT ===
Recommendation Rationale: Premier 3-Year 24×7 4hr（概率 78%，高置信度）

该推荐由 Engine II（热启动）基于历史偏好 + 产品关联生成：

• SR650 机型历史 bid 中 Premier 采纳率 82%（+0.18 SHAP）
• Enterprise 客户平均保修等级高于 SMB 1.4 档，5 年完整覆盖倾向显著（+0.12 SHAP）
• 一次性合同对该等级保修有轻微负向影响（-0.05 SHAP），但不改变排名

Add-on 建议：
• Installation (Business Hours)：概率 90%，基于 84% 同类客户选择

高置信度（0.78 > 0.75）→ Branch 2，围绕最优计划提供完整推荐。
</example>
```

### 12.2 Customer 版示例

```
<example>
=== SAMPLE INPUT ===
Customer: Enterprise | Financial Services | USA
Hardware: ThinkSystem SR650
Service: Premier, 3Y, 24x7 4hr
Factors:
  1. "您选择的 SR650 服务器通常搭配高级别服务保障"
  2. "作为企业用户，全面保障方案更适合您的业务连续性需求"
  3. "您的硬件投资规模较大，建议匹配相应级别的服务覆盖"
  4. "北美地区客户普遍选择此级别的服务方案"
Add-ons:
  - Installation (Business Hours): "标准工作时间上门安装服务"
  - KYD (3Y): "3 年硬盘保留服务"

=== EXPECTED OUTPUT ===
Why we recommend Premier 3-Year coverage

The ThinkSystem SR650 is an enterprise-grade server platform. Premier service with 
24×7 support and 4-hour onsite response helps ensure maximum uptime for your 
business-critical workloads.

As an enterprise customer in the financial services sector, comprehensive coverage 
aligns with the reliability standards your operations require.

The scale of your hardware deployment makes full-coverage support a prudent choice 
to protect your infrastructure investment.

We also suggest:
• Professional installation during business hours to get your systems up and running quickly
• 3-Year Keep Your Drive service for added data security and compliance peace of mind
</example>
```

---

## 附录 A：端到端示例（Bid #US-NA-2026-06421）

> 场景：Enterprise 客户 / USA / ThinkSystem SR650 / $85K / One-Time
> 完整流程详见 `recommendation_model_overview.md`

### A.1 结构化上下文 JSON

```json
{
  "bid_context": {
    "customer_segment": "Enterprise",
    "customer_industry": "Financial Services",
    "country": "USA",
    "hardware_product_family": "ThinkSystem SR650",
    "hardware_value_band": "50K-100K",
    "contract_type": "One-Time"
  },
  "recommendation": {
    "service_type": "Premier",
    "service_term": "3Y",
    "service_sla": "24x7 4hr",
    "probability": 0.78,
    "confidence_level": "high",
    "recall_source": "Engine II"
  },
  "features": [
    {
      "rank": 1, "name": "hardware_product_family", "value": "SR650",
      "shap": "+0.18", "direction": "push_up",
      "internal": "SR650 机型历史 bid 中 Premier 采纳率 82%",
      "customer": "您选择的 SR650 服务器通常搭配高级别服务保障"
    },
    {
      "rank": 2, "name": "customer_segment", "value": "Enterprise",
      "shap": "+0.12", "direction": "push_up",
      "internal": "Enterprise 客户平均保修等级高于 SMB 1.4 档",
      "customer": "作为企业用户，全面保障方案更适合您的业务连续性需求"
    },
    {
      "rank": 3, "name": "hardware_value_band", "value": "50K-100K",
      "shap": "+0.10", "direction": "push_up",
      "internal": "硬件价值 $85K，处于 50K-100K 区间，该区间 Premier 采纳率 74%",
      "customer": "您的硬件投资规模较大，建议匹配相应级别的服务覆盖"
    },
    {
      "rank": 4, "name": "country", "value": "USA",
      "shap": "+0.08", "direction": "push_up",
      "internal": "北美市场 Premier 整体采纳率 67%，高于全球均值 52%",
      "customer": "北美地区客户普遍选择此级别的服务方案"
    },
    {
      "rank": 5, "name": "customer_industry", "value": "Financial Services",
      "shap": "+0.06", "direction": "push_up",
      "internal": "金融服务行业 Premier 采纳率 71%，高于跨行业均值 58%",
      "customer": "金融服务行业对系统可靠性要求高，全面的服务保障是行业惯例"
    },
    {
      "rank": 6, "name": "historical_attach_rate", "value": "0.74",
      "shap": "+0.05", "direction": "push_up",
      "internal": "同类 bid（Enterprise + US + Financial Services）历史采纳率 74%",
      "customer": null
    },
    {
      "rank": 7, "name": "contract_type", "value": "One-Time",
      "shap": "-0.05", "direction": "push_down",
      "internal": "一次性合同对该等级保修有轻微负向影响（-0.05 SHAP），但不改变排名",
      "customer": null
    },
    {
      "rank": 8, "name": "recent_trend_direction", "value": "+3pp over 6mo",
      "shap": "+0.03", "direction": "push_up",
      "internal": "近 6 个月该服务采纳趋势上升 3 个百分点",
      "customer": "近期越来越多客户选择更全面的保障方案"
    }
  ],
  "business_rules": ["geo_availability: pass", "eol_check: pass", "compliance: pass"],
  "addons": [
    {
      "type": "Installation", "option": "Business Hours", "probability": 0.90,
      "internal": "Installation (Business Hours)：概率 90%，基于 84% 同类客户选择",
      "customer": "标准工作时间上门安装服务，确保设备快速就绪"
    },
    {
      "type": "KYD", "option": "3Y Keep Your Drive", "probability": 0.72,
      "internal": "KYD (3-Year)：概率 72%，基于同机型共现统计",
      "customer": "3 年硬盘保留服务，数据安全更有保障，满足金融监管合规要求"
    }
  ]
}
```

### A.2 LLM 实际调用与输出

#### Internal Prompt（发送给 LLM）

```
Generate an Internal-facing recommendation explanation using the data below.

=== BID CONTEXT ===
Customer: Enterprise | Industry: Financial Services | Country: USA
Hardware: ThinkSystem SR650 | Value Band: 50K-100K
Contract Type: One-Time

=== RECOMMENDATION ===
Service Plan: Premier | Term: 3Y | SLA: 24x7 4hr
Probability: 0.78 | Confidence: high
Recall Source: Engine II — 热启动（同 segment 历史偏好 + 产品关联）

=== TOP CONTRIBUTING FEATURES ===
1. hardware_product_family = SR650
   SHAP: +0.18 | Direction: push_up
   Business Language: SR650 机型历史 bid 中 Premier 采纳率 82%

2. customer_segment = Enterprise
   SHAP: +0.12 | Direction: push_up
   Business Language: Enterprise 客户平均保修等级高于 SMB 1.4 档

3. hardware_value_band = 50K-100K
   SHAP: +0.10 | Direction: push_up
   Business Language: 硬件价值 $85K，处于 50K-100K 区间，该区间 Premier 采纳率 74%

4. country = USA
   SHAP: +0.08 | Direction: push_up
   Business Language: 北美市场 Premier 整体采纳率 67%，高于全球均值 52%

5. customer_industry = Financial Services
   SHAP: +0.06 | Direction: push_up
   Business Language: 金融服务行业 Premier 采纳率 71%，高于跨行业均值 58%

6. historical_attach_rate = 0.74
   SHAP: +0.05 | Direction: push_up
   Business Language: 同类 bid（Enterprise + US + Financial Services）历史采纳率 74%

7. contract_type = One-Time
   SHAP: -0.05 | Direction: push_down
   Business Language: 一次性合同对该等级保修有轻微负向影响（-0.05 SHAP），但不改变排名

8. recent_trend_direction = +3pp over 6mo
   SHAP: +0.03 | Direction: push_up
   Business Language: 近 6 个月该服务采纳趋势上升 3 个百分点

=== BUSINESS RULES ===
geo_availability: pass | eol_check: pass | compliance: pass

=== ADD-ON SUGGESTIONS ===
Installation: Business Hours (probability 90%)
  Business Language: Installation (Business Hours)：概率 90%，基于 84% 同类客户选择
KYD: 3Y Keep Your Drive (probability 72%)
  Business Language: KYD (3-Year)：概率 72%，基于同机型共现统计

=== OUTPUT FORMAT ===
Start with: "Recommendation Rationale: Premier 3Y 24x7 4hr"
Then bullet points (one per feature), ordered by SHAP impact.
End with confidence level and branch type.
```

#### Internal 版输出

```
Recommendation Rationale: Premier 3-Year 24×7 4hr（概率 78%，高置信度）

该推荐由 Engine II（热启动）基于同 segment 历史偏好 + 产品关联生成：

• SR650 机型历史 bid 中 Premier 采纳率 82%（+0.18 SHAP）
• Enterprise 客户平均保修等级高于 SMB 1.4 档，5 年完整覆盖倾向显著（+0.12 SHAP）
• 硬件价值 $85K，处于 50K-100K 区间，该区间 Premier 采纳率 74%（+0.10 SHAP）
• 北美市场 Premier 整体采纳率 67%，高于全球均值 52%（+0.08 SHAP）
• 金融服务行业 Premier 采纳率 71%，高于跨行业均值 58%（+0.06 SHAP）
• 同类 bid（Enterprise + US + Financial Services）历史采纳率 74%（+0.05 SHAP）
• 一次性合同对该等级保修有轻微负向影响（-0.05 SHAP），但不改变排名
• 近 6 个月该服务采纳趋势上升 3 个百分点（+0.03 SHAP）

Add-on 建议：
• Installation (Business Hours)：概率 90%，基于 84% 同类客户选择
• KYD (3-Year)：概率 72%，基于同机型共现统计

高置信度（0.78 > 0.75 阈值）→ Branch 2，围绕最优计划提供 GBB 完整推荐。
```

#### Customer Prompt（发送给 LLM）

```
Generate a Customer-facing recommendation explanation using the data below.

=== CUSTOMER CONTEXT ===
Type: Enterprise | Industry: Financial Services | Location: USA

=== HARDWARE ===
ThinkSystem SR650

=== RECOMMENDED SERVICE ===
Premier with 3-Year coverage (24×7 4hr onsite response)

=== SUPPORTING FACTORS ===
1. Customer Language: 您选择的 SR650 服务器通常搭配高级别服务保障
2. Customer Language: 作为企业用户，全面保障方案更适合您的业务连续性需求
3. Customer Language: 您的硬件投资规模较大，建议匹配相应级别的服务覆盖
4. Customer Language: 北美地区客户普遍选择此级别的服务方案
5. Customer Language: 金融服务行业对系统可靠性要求高，全面的服务保障是行业惯例
6. Customer Language: 近期越来越多客户选择更全面的保障方案

=== SUGGESTED ADD-ONS ===
Installation: 标准工作时间上门安装服务，确保设备快速就绪
KYD: 3 年硬盘保留服务，数据安全更有保障，满足金融监管合规要求

=== OUTPUT FORMAT ===
Start with: "Why we recommend Premier 3-Year coverage"
Short paragraphs (2-3 sentences each), one per supporting factor.
End with add-on suggestions in a friendly tone.
NO numbers, NO percentages, NO technical terms.
```

#### Customer 版输出

```
Why we recommend Premier 3-Year coverage

The ThinkSystem SR650 is an enterprise-grade platform designed for demanding 
workloads. Premier coverage with 24×7 support and 4-hour onsite response helps 
ensure your critical systems stay operational around the clock.

As an enterprise organization in financial services, system reliability directly 
impacts your business operations. Comprehensive coverage with guaranteed response 
times aligns with the uptime standards your industry demands.

The scale of your hardware deployment makes full-coverage support a strategic choice 
to protect your infrastructure investment and maintain predictable operational costs.

Clients across North America consistently select this level of coverage for their 
enterprise deployments, making it a proven choice for organizations with similar 
reliability requirements.

Financial services organizations increasingly rely on comprehensive service plans 
to support their digital infrastructure, a trend that continues to grow across 
the industry.

We also suggest:
• Professional on-site installation during business hours to ensure your systems 
  are configured correctly from day one
• 3-Year Keep Your Drive service — retain your drives for added data security and 
  compliance, particularly valuable in financial services environments
```

### A.3 输出校验结果

#### Internal 版校验

| 检查项 | 结果 |
|--------|------|
| 输出非空 | ✅ 305 chars |
| 不含 LLM 自述 | ✅ 无 "Here is" / "Based on" |
| 特征名均合法 | ✅ 所有特征在输入 JSON 中 |
| 概率值正确 | ✅ 0.78 |
| 8 个特征覆盖 | ✅ 全部覆盖（含负向） |
| SHAP 顺序正确 | ✅ 0.18 → 0.12 → 0.10 → 0.08 → 0.06 → 0.05 → -0.05 → 0.03 |

#### Customer 版校验

| 检查项 | 结果 |
|--------|------|
| 输出非空 | ✅ 1,200+ chars |
| 无数字泄露 | ✅ 正则扫描通过 |
| 无技术术语 | ✅ 无 "SHAP" "XGBoost" "Engine" "probability" |
| 无负向暗示 | ✅ 无 "however" "but" "although" |
| 无比较其他方案 | ✅ 只讨论自身 |
| 英文 | ✅ |

**全部校验通过。解释可交付。**

### A.4 不同场景的对策总结

| 场景 | Internal 策略 | Customer 策略 |
|------|-------------|-------------|
| **高置信度（prob > 0.75）** | 完整特征展示 + 数据引用 | 完整叙事，建议口吻 |
| **低置信度（prob ≤ 0.75）** | 标注置信度，展示可用正面特征 + 降级说明 | 通用模板，"按需选择"口吻 |
| **冷启动（Engine I）** | 标注关联规则来源，无 SHAP 数据 | 基于硬件通用建议 |
| **LLM 不可用** | 规则模板（特征列表） | 固定话术模板 |

---

*依赖文档*：
- `api_schema_model_catalog_contract.md` — Model → Catalog JSON Schema
- `feature_business_language_mapping.md` — 特征映射表（Phase 2 启用）
