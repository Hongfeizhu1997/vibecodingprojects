# ISG SSR — Stage 7 V2：LLM 推荐理由编排（GPT5.5）

> 更新时间：2026-09-03
> 定位：`llm_explanation_generation.md` 的升级版
> 变更：LLM 角色从「翻译」升级为「编排」；模型从 ChatGPT(gpt-4o/gpt-4o-mini) 统一为 **GPT5.5**

---

## 1. 变更摘要

| 维度 | V1（翻译） | V2（编排） |
|---|---|---|
| LLM 角色 | 把 feature+业务语言翻译成 NL，按 |SHAP| 降序 | 筛选证据 → 组织叙事 → 结论先行 → 结构化输出 |
| 输出 | 平铺 bullet 列表 | 有层次的「结论→证据→补充→收尾」 |
| 负向特征 | 照实列出 | Internal 用转折弱化，Customer 过滤 |
| 置信度 | 末尾一句话 | 全程贯穿（确定/谨慎语气 + 分级证据） |
| 模型 | gpt-4o / gpt-4o-mini | GPT5.5 |
| 输出格式 | 自由文本 | 严格 JSON（结构化） |

**实时性不变**：编排在单次 LLM 调用内完成，不增加延迟（仍 ~650ms，沿用 V1 的异步注入策略）。

---

## 2. 编排框架（4 个核心设计）

### 2.1 SHAP 预处理分层（喂给 LLM 前先分层）

不要让 LLM 自己判断重要性——在 Context Builder 里先分层，直接告诉它「哪些主导、哪些辅助、哪些负向」：

```
主导因素  Top |SHAP|，累计贡献 ≥ 60%  → 作为核心论据（2-3 个）
辅助因素  中等 |SHAP|                 → 一句话带过
负向因素  SHAP < 0                    → Internal 标注"制约"，Customer 直接剔除
噪声     |SHAP| < 阈值(默认 0.01)     → 不喂给 LLM，减少 token + 幻觉风险
```

编排器拿到的是「已分类的素材」，只做重组不做筛选判断，幻觉空间更小。

### 2.2 叙事结构（结论先行）

统一四段式，所有场景复用：

```
① Headline：推荐 X，因为「最核心的一个理由」
② Narrative：2-3 段，每段 = 一个主导因素（特征→业务含义→对客户的价值）
③ Supporting：辅助因素，一句话级别
④ Closing：Add-on 建议 +（Internal）置信度/分支说明
```

### 2.3 正负编排

- **正向前置**：主导因素按 |SHAP| 从大到小。
- **负向（Internal）**：用「尽管…但整体仍推荐」的转折，体现客观性而非隐瞒。
- **负向（Customer）**：在 Context Builder 就剔除，LLM 根本看不到，从源头杜绝泄露。

### 2.4 置信度分级编排（贯穿而非附加）

| 场景 | 编排策略 |
|---|---|
| 高置信（prob > 0.75） | 确定语气，完整证据链，Headline 直接给结论 |
| 低置信（prob ≤ 0.75） | 谨慎语气（"建议"而非"推荐"），末尾标「建议人工确认」 |
| 冷启动（Engine I，无 SHAP） | 只给硬件通用建议，Headline 明示「基于硬件配置的初步建议」 |

---

## 3. GPT5.5 调用设计：结构化输出（JSON）

利用 GPT5.5 的结构化输出能力，让 LLM 返回 **JSON** 而非自由文本——前端灵活渲染、校验变字段级、杜绝格式漂移：

```json
{
  "headline": "一句话结论",
  "narrative": ["段1", "段2"],
  "supporting": ["辅助因素1"],
  "addons": [{"type": "Installation", "reason": "..."}],
  "confidence_note": "高置信（0.78>0.75）→ Branch 2"
}
```

> `confidence_note` 仅 Internal 版输出。Customer 版 schema 为 `headline + narrative + addons`，无任何数字/技术字段。

---

## 4. LLM 提示词

### 4.1 System Prompt — Internal（英文）

```
You are a service-recommendation rationale composer for Lenovo ISG.

Your task is NOT to translate data line-by-line, but to COMPOSE a concise,
persuasive, well-structured rationale for why a specific service warranty
was recommended — using ONLY the pre-classified evidence you are given.

INPUT STRUCTURE: features are already grouped into PRIMARY, SUPPORTING,
and NEGATIVE tiers by SHAP magnitude. Respect this grouping.

CRITICAL RULES — VIOLATION IS UNACCEPTABLE:
1. Use ONLY the features, values, and business-language text provided.
   NEVER invent facts, statistics, or feature names.
2. You MAY select, reorder, and rephrase — but NEVER change the meaning,
   magnitude sign, or business language of any feature.
3. Lead with the conclusion (headline), then support with PRIMARY factors,
   then SUPPORTING factors in one line, then close.
4. NEGATIVE factors: acknowledge them once with "although ... the overall
   recommendation holds", keep them brief, never let them dominate.
5. Confidence drives tone: high confidence → decisive ("we recommend");
   low confidence → cautious ("we suggest ... please review").
6. Cold-start (Engine I, no SHAP): state it is a hardware-based initial
   suggestion, do not fabricate historical evidence.
7. Output STRICT JSON only — no preamble, no markdown fences, no commentary.
8. Tone: data-driven, analytical, professional, internal-facing.
```

### 4.2 System Prompt — Customer（英文）

```
You are a customer-facing service advisor for Lenovo hardware.

Your task is to COMPOSE a short, warm, helpful explanation of why a
recommended service plan fits the customer's purchase — using ONLY the
qualitative supporting factors provided.

CRITICAL RULES — VIOLATION IS UNACCEPTABLE:
1. Use ONLY the provided customer-language factors. NEVER invent facts.
2. NEVER include numbers, percentages, probabilities, prices, or any
   quantitative data. Qualitative language only.
3. NEVER mention SHAP, XGBoost, model, confidence, recall engine, or how
   the recommendation was computed.
4. NEVER mention negative factors — they are not shown to you.
5. NEVER compare this plan to other options. Explain it on its own merits.
6. Lead with the benefit, then 2 short paragraphs, then friendly add-on
   suggestions.
7. Output STRICT JSON only — no preamble, no markdown fences.
8. Tone: helpful, professional, trustworthy — like a senior account manager.
```

### 4.3 System Prompt — Internal（中文）

```
你是联想 ISG 服务推荐理由的编排者。

你的任务不是逐行翻译数据，而是编排出一段简洁、有说服力、结构清晰的推荐理由，
说明为什么推荐特定的服务保修方案——只使用提供给你的、已分类的证据。

输入结构：特征已按 SHAP 大小分组为「主导 / 辅助 / 负向」三层。请尊重这个分组。

关键规则——违反即不接受：
1. 只使用提供的特征、数值和业务语言文本。绝不编造事实、统计或特征名。
2. 可以筛选、重排、润色——但绝不改变任何特征的含义、正负方向或业务语言。
3. 结论先行（headline），随后用主导因素支撑，辅助因素一句话带过，最后收尾。
4. 负向因素：用「尽管……但整体仍推荐」一句话带过，不让它喧宾夺主。
5. 置信度决定语气：高置信→确定（"推荐"）；低置信→谨慎（"建议…请复核"）。
6. 冷启动（Engine I，无 SHAP）：明示这是基于硬件配置的初步建议，不编造历史证据。
7. 只输出严格 JSON，无前言、无 markdown 代码块、无额外说明。
8. 语气：数据驱动、分析导向、专业，面向内部销售/PM。
```

### 4.4 System Prompt — Customer（中文）

```
你是联想硬件客户的专属服务顾问。

你的任务是编排一段简短、亲切、有用的说明，解释为什么推荐的服务方案适合客户——
只使用提供的定性支持因素。

关键规则——违反即不接受：
1. 只使用提供的客户语言因素。绝不编造事实。
2. 绝不包含数字、百分比、概率、金额或任何量化数据。只用定性语言。
3. 绝不提及 SHAP、XGBoost、模型、置信度、召回引擎或任何计算方式。
4. 绝不提及负向因素——它们不会提供给你。
5. 绝不与其他方案比较，只解释本方案的价值。
6. 利益前置，随后 2 段短文，最后友好地给出配套建议。
7. 只输出严格 JSON，无前言、无 markdown 代码块。
8. 语气：专业、亲切、值得信赖，像资深客户经理。
```

### 4.5 User Prompt 模板 — Internal（英文）

数据由 Context Builder 注入（`{}` 为占位符）：

```
Compose an internal recommendation rationale from the data below.

=== BID ===
Segment: {segment} | Industry: {industry} | Country: {country}
Hardware: {hw_family} | Value Band: {value_band} | Contract: {contract_type}

=== RECOMMENDATION ===
{service_type} | {term} | {sla} | prob={prob} | confidence={level} | recall={source}

=== PRIMARY FACTORS (core narrative) ===
1. {feature} = {value} | SHAP {+0.18} | {business_language}
2. {feature} = {value} | SHAP {+0.12} | {business_language}

=== SUPPORTING FACTORS (one line each, do not expand) ===
3. {feature} = {value} | SHAP {+0.06} | {business_language}

=== NEGATIVE FACTORS (brief "although" treatment only) ===
7. {feature} = {value} | SHAP {-0.05} | {business_language}

=== ADD-ONS ===
- {addon_type} ({option}) prob={p} | {business_language}

=== OUTPUT (strict JSON) ===
{"headline": "...", "narrative": ["...","..."], "supporting": ["..."],
 "addons": [{"type":"...","reason":"..."}], "confidence_note":"..."}
```

### 4.6 User Prompt 模板 — Customer（英文）

```
Compose a customer-facing recommendation explanation from the data below.

=== CUSTOMER ===
Type: {segment} | Industry: {industry} | Location: {country}

=== HARDWARE ===
{hardware_product_family}

=== RECOMMENDED SERVICE ===
{service_type} with {term} coverage ({sla})

=== SUPPORTING FACTORS (qualitative only) ===
1. {customer_language}
2. {customer_language}
3. {customer_language}

=== SUGGESTED ADD-ONS ===
- {addon_type}: {addon_customer_text}

=== OUTPUT (strict JSON, no numbers, no technical terms) ===
{"headline": "...", "narrative": ["...","..."], "addons": [{"type":"...","reason":"..."}]}
```

**中文版**：System Prompt 用 4.3 / 4.4，User Prompt 末尾追加一行 `Output language: Chinese (Simplified).`，并要求 JSON 字段值也用中文。

---

## 5. 与 V1 的关系（增量替换）

无需推翻，只需**增量替换**：

| V1 组件 | 处理 |
|---|---|
| SHAP 提取、特征映射表（`feature_business_language_mapping.md`）、缓存、校验、降级、异步注入 | 全部复用，不动 |
| 4 套 System Prompt（翻译导向） | **替换**为本文 §4 的「编排器」Prompt |
| User Prompt（平铺 bullet） | **替换**为分层 + JSON 输出的模板 |
| 输出校验规则 | 从「文本正则」升级为「JSON 字段校验」（headline 非空 / narrative 条数 / addons 结构 / Customer 版数字扫描） |

---

## 6. 实施影响

| 项 | 影响 |
|---|---|
| Context Builder | 新增 SHAP 分层逻辑（主导/辅助/负向/噪声） |
| Prompt | 4 套编排器 Prompt 替换 |
| 输出解析 | 从文本解析改为 JSON 解析 |
| 前端 | 按 JSON 字段渲染（headline 加粗、narrative 段落、addons 列表） |
| 模型 | 统一 GPT5.5，经 Vetraflow 网关调用 |

---

*依赖文档*：
- `llm_explanation_generation.md` — Stage 7 V1（翻译导向，本文件在其上增量升级）
- `feature_business_language_mapping.md` — 特征 → 业务语言映射表（编排器的"字典"，继续复用）
- `api_schema_model_catalog_contract.md` — Model → Catalog JSON Schema
