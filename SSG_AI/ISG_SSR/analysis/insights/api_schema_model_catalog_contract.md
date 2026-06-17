# ISG SSR — Model → Catalog API 契约

> 版本：V1 · 2026-06-17
> 用途：XGBoost 推理输出到 Catalog 消费的结构化 JSON Schema
> 状态：方案阶段，待评审

---

## 1. 顶层结构

每次推荐调用返回一个 JSON 对象，包含 bid 级别的元信息 + N 个推荐计划（Base Warranty）+ 各自的 Add-on 建议 + SHAP 特征贡献。

```json
{
  "bid_id": "string",
  "model_version": "string",
  "timestamp": "ISO8601",
  "recall": { ... },
  "recommendations": [ ... ],
  "addon_recommendations": [ ... ]
}
```

---

## 2. 字段定义

### 2.1 Recall 信息

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `source` | `"engine_i" \| "engine_ii"` | ✅ | Engine I = 冷启动（关联规则），Engine II = 热启动（Popularity + Association） |
| `candidate_count` | `integer` | ✅ | 进入排序的候选集大小（如 56） |
| `features_used` | `integer` | ✅ | 实际参与推理的特征数（如 48，部分特征因稀疏性被排除） |

### 2.2 Recommendation 对象

每个 `recommendations[i]` 描述一个 Base Warranty Plan：

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `rank` | `integer` | ✅ | 排序位置（1-based），按 probability 降序 |
| `service_type` | `string` | ✅ | `"Premier"` / `"Base"` / `"Enhanced"` |
| `warranty_term` | `string` | ✅ | `"1Y"` / `"2Y"` / `"3Y"` / `"4Y"` / `"5Y"` |
| `warranty_sla` | `string` | ✅ | `"24x7 4hr"` / `"NBD"` / `"24x7 2hr"` |
| `probability` | `float` | ✅ | 预测概率，范围 [0, 1]，所有 plans 的 prob 之和 = 1 |
| `confidence_level` | `"high" \| "medium" \| "low"` | ✅ | `high` = prob > 0.75, `medium` = 0.5–0.75, `low` = <0.5 |
| `shap_contributions` | `ShapContribution[]` | ✅ | 对本 plan 的 SHAP 特征贡献，按 \|shap_value\| 降序排列 |

### 2.3 SHAP Contribution 对象

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `rank` | `integer` | ✅ | SHAP 影响排名（1 = 最大影响） |
| `feature_name` | `string` | ✅ | 特征名（如 `"customer_segment"`） |
| `feature_value` | `string` | ✅ | **已离散化**的特征值（如 `"Enterprise"` 而非原始编码） |
| `shap_value` | `float` | ✅ | SHAP 贡献值，正 = push_up，负 = push_down |
| `direction` | `"push_up" \| "push_down"` | ✅ | 方向 |
| `business_language` | `object` | ⚠️ | 预留字段，Phase 1 映射表完成后填充（见 §5） |

> **注意**：`business_language` 待特征映射表完工后由上游填充。Phase 1（映射表构建前）此字段为 `null`，Catalog 仍可使用 `feature_name` + `feature_value` 做规则模板降级解释。映射表完成后，此字段包含 `{"internal": "...", "customer": "..."}`。

### 2.4 Add-on Recommendation 对象

每个 `addon_recommendations[i]` 描述一个 Add-on 模块的推荐：

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `addon_type` | `string` | ✅ | `"Installation"` / `"KYD"` / `"CO2_Offset"` / `"CSR"` |
| `options` | `AddonOption[]` | ✅ | 该模块下的互斥选项，按概率降序 |
| `selection_threshold` | `float` | ❌ | 激活阈值（可选），低于此值的 add-on 不推荐 |

### 2.5 Addon Option 对象

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `rank` | `integer` | ✅ | 排序 |
| `option_code` | `string` | ✅ | 选项编码（如 `"QA0H"`） |
| `option_label` | `string` | ✅ | 可读标签（如 `"Installation (Business Hours)"`） |
| `probability` | `float` | ✅ | 该选项的概率，同模块内所有选项 prob 之和 = 1 |
| `shap_contributions` | `ShapContribution[]` | ⚠️ | Add-on 子模型的 SHAP 特征贡献（约 5-8 个特征） |

---

## 3. 完整 JSON 示例

```json
{
  "bid_id": "US-NA-2026-06421",
  "model_version": "xgboost-v2.3.1-20260601",
  "timestamp": "2026-06-17T14:30:00Z",
  "recall": {
    "source": "engine_ii",
    "candidate_count": 56,
    "features_used": 48
  },
  "recommendations": [
    {
      "rank": 1,
      "service_type": "Premier",
      "warranty_term": "3Y",
      "warranty_sla": "24x7 4hr",
      "probability": 0.78,
      "confidence_level": "high",
      "shap_contributions": [
        {
          "rank": 1,
          "feature_name": "hardware_product_family",
          "feature_value": "SR650",
          "shap_value": 0.18,
          "direction": "push_up",
          "business_language": null
        },
        {
          "rank": 2,
          "feature_name": "customer_segment",
          "feature_value": "Enterprise",
          "shap_value": 0.12,
          "direction": "push_up",
          "business_language": null
        },
        {
          "rank": 3,
          "feature_name": "hardware_value_band",
          "feature_value": "50K-100K",
          "shap_value": 0.10,
          "direction": "push_up",
          "business_language": null
        },
        {
          "rank": 4,
          "feature_name": "country",
          "feature_value": "USA",
          "shap_value": 0.08,
          "direction": "push_up",
          "business_language": null
        },
        {
          "rank": 5,
          "feature_name": "contract_type",
          "feature_value": "One-Time",
          "shap_value": -0.05,
          "direction": "push_down",
          "business_language": null
        },
        {
          "rank": 6,
          "feature_name": "customer_industry",
          "feature_value": "Financial Services",
          "shap_value": 0.06,
          "direction": "push_up",
          "business_language": null
        },
        {
          "rank": 7,
          "feature_name": "historical_attach_rate",
          "feature_value": "0.74",
          "shap_value": 0.05,
          "direction": "push_up",
          "business_language": null
        },
        {
          "rank": 8,
          "feature_name": "recent_trend_direction",
          "feature_value": "up_3pp_6mo",
          "shap_value": 0.03,
          "direction": "push_up",
          "business_language": null
        }
      ]
    },
    {
      "rank": 2,
      "service_type": "Premier",
      "warranty_term": "5Y",
      "warranty_sla": "NBD",
      "probability": 0.12,
      "confidence_level": "low",
      "shap_contributions": [
        {
          "rank": 1,
          "feature_name": "hardware_product_family",
          "feature_value": "SR650",
          "shap_value": 0.08,
          "direction": "push_up",
          "business_language": null
        },
        {
          "rank": 2,
          "feature_name": "customer_segment",
          "feature_value": "Enterprise",
          "shap_value": -0.06,
          "direction": "push_down",
          "business_language": null
        },
        {
          "rank": 3,
          "feature_name": "contract_type",
          "feature_value": "One-Time",
          "shap_value": -0.04,
          "direction": "push_down",
          "business_language": null
        }
      ]
    },
    {
      "rank": 3,
      "service_type": "Base",
      "warranty_term": "3Y",
      "warranty_sla": "24x7 4hr",
      "probability": 0.06,
      "confidence_level": "low",
      "shap_contributions": []
    }
  ],
  "addon_recommendations": [
    {
      "addon_type": "Installation",
      "options": [
        {
          "rank": 1,
          "option_code": "QA0H",
          "option_label": "Installation (Business Hours)",
          "probability": 0.90,
          "shap_contributions": [
            {
              "rank": 1,
              "feature_name": "hardware_value_band",
              "feature_value": "50K-100K",
              "shap_value": 0.22,
              "direction": "push_up",
              "business_language": null
            }
          ]
        },
        {
          "rank": 2,
          "option_code": "QA0J",
          "option_label": "Installation (Off Shift Hours)",
          "probability": 0.10,
          "shap_contributions": []
        }
      ]
    },
    {
      "addon_type": "KYD",
      "options": [
        {
          "rank": 1,
          "option_code": "QD3Y",
          "option_label": "3Y Keep Your Drive",
          "probability": 0.72,
          "shap_contributions": [
            {
              "rank": 1,
              "feature_name": "customer_industry",
              "feature_value": "Financial Services",
              "shap_value": 0.15,
              "direction": "push_up",
              "business_language": null
            }
          ]
        },
        {
          "rank": 2,
          "option_code": "QD5Y",
          "option_label": "5Y Keep Your Drive",
          "probability": 0.28,
          "shap_contributions": []
        }
      ]
    },
    {
      "addon_type": "CO2_Offset",
      "options": [
        {
          "rank": 1,
          "option_code": "CO2_YES",
          "option_label": "CO₂ Offset",
          "probability": 0.48,
          "shap_contributions": []
        }
      ]
    }
  ]
}
```

---

## 4. 概率约束

| 约束 | 验证方式 |
|------|---------|
| `sum(recommendations[*].probability) == 1.00` | 浮点容差 ±0.01 |
| 每个 add-on 模块内 `sum(options[*].probability) == 1.00` | 同上 |
| `recommendations` 按 `probability` 降序 | 遍历验证 |
| `shap_contributions` 按 `abs(shap_value)` 降序 | 遍历验证 |

---

## 5. business_language 字段（Phase 2 填充）

当特征映射表完成后，`business_language` 字段从 `null` 变为：

```json
{
  "business_language": {
    "internal": "SR650 机型历史 bid 中 Premier 采纳率 82%",
    "customer": "您选择的 SR650 服务器通常搭配高级别服务保障"
  }
}
```

**Phase 1 过渡策略**：`business_language` 为 `null` 时，Catalog/LLM 可使用规则模板降级生成解释（见 `prompt_engineering_spec.md` §6 降级策略）。

---

## 6. 多语言字段预留

为支持多语言 Customer 版解释，`business_language` 完整结构设计为：

```json
{
  "business_language": {
    "internal": { "en": "...", "zh": "..." },
    "customer": { "en": "...", "zh": "..." }
  }
}
```

Phase 1 仅填充英文，中文在映射表二期补充。

---

## 7. Catalog 消费流程（含 LLM 调用）

```
Model API Response (本 Schema)
        ↓
Catalog Product Logic Filter
  · Region Availability · Contract Constraints
  · Product Lifecycle · Price Thresholds
        ↓
Decision Gate: max_prob > 0.75?
   ↙ YES (Branch 2)              ↘ NO (Branch 1)
Select top plan                  Sort by price
        ↓                              ↓
Stage 7: LLM Explanation        Stage 7 Lite: 降级模板
  ├── Build Context (extract     └── 规则模板解释
  │   bid + top plan + SHAP)
  ├── Feature Mapping Lookup
  ├── Parallel LLM Calls:
  │   ├── Internal Prompt → Vetraflow+ChatGPT
  │   └── Customer Prompt → Vetraflow+ChatGPT
  ├── Output Validation
  │   ├── Internal: 特征名校验 + 概率值校验
  │   └── Customer: 数字泄露检测 + 术语黑名单
  └── Return explanations
        ↓
Cache: (bid_hash, rec_hash) → explanations
        ↓
GBB Frontend: 3 tiers + Internal/Customer explanation each
```

---

*Next: 技术方案文档更新（Vetraflow+ChatGPT 集成、多语言 Prompt、实时生成延迟分析）*
