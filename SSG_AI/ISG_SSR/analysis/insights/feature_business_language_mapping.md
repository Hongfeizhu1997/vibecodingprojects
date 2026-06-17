# ISG SSR — 特征 → 业务语言映射表

> 用途：LLM 生成推荐理由时的"翻译字典"，将技术特征名转为业务人员可理解的表述
> 版本：V1 Draft · 2026-06-08
> 状态：待产品/PM 审核

---

## 映射规则

1. **Internal 版**：可引用具体数值、百分比、SHAP 方向。语气分析导向。
2. **Customer 版**：纯定性语言，不出现数字/百分比/技术术语。语气建议导向。
3. **正贡献特征（SHAP > 0）**：解释为"支持推荐的因素"，两版都展示。
4. **负贡献特征（SHAP < 0）**：仅在 Internal 版展示为"制约因素"。Customer 版不展示。
5. **特征值**：LLM 使用本表中的预定义表述，不得自行解释特征含义。

---

## 1. 硬件维度（Hardware）

| 特征名 | Internal 表述模板 | Customer 表述模板 |
|--------|-----------------|-----------------|
| `hardware_product_family` | `{value}` 机型历史 bid 中，此类保修采纳率为 `{rate}%` | 您选择的 `{value}` 服务器通常搭配此类服务保障 |
| `hardware_machine_type` | `{value}` 型号与该服务组合的历史匹配度 `{rate}%` | 该机型普遍适配此级别服务方案 |
| `hardware_config_tier` | 设备配置为 `{value}` 级别，同级别配置的 Premier 选用率比标准配置高 `{diff}` 个百分点 | 您的设备配置级别较高，高性能硬件通常匹配更全面的保障 |
| `hardware_generation` | 第 `{value}` 代产品，该代 Premier 采纳率 `{rate}%` | 新一代硬件我们建议匹配更新的服务标准 |
| `hardware_form_factor` | `{value}` 机型（`{form}` 形态），适配性检查通过 | 您的设备形态适合此服务方案 |

**负向特征（仅 Internal）**：

| 特征名 | Internal 表述模板 |
|--------|-----------------|
| `hardware_product_family`（负） | `{value}` 机型历史 Premier 采纳率仅 `{rate}%`，多数客户选择更基础方案 |
| `hardware_eol_status` | 该硬件已进入 EOL 周期，新保修的性价比可能不如替换方案 |

---

## 2. 客户维度（Customer）

| 特征名 | Internal 表述模板 | Customer 表述模板 |
|--------|-----------------|-----------------|
| `customer_segment` | `{value}` 客户，该 segment 平均保修等级为 `{avg_tier}`，高于/低于整体均值 `{diff}` 档 | 作为 `{value}` 客户，您的业务规模适合此级别的服务覆盖 |
| `customer_industry` | `{value}` 行业，该行业 Premier 采纳率 `{rate}%` | `{value}` 行业的客户通常选择此类保障方案以降低运营风险 |
| `customer_size_dmu` | DMU 规模 `{value}`，大型 DMU 倾向于选择更全面的保修（+`{shap}`） | 您的团队规模较大，全面的服务支持可以降低管理复杂度 |
| `customer_tenure` | 合作年限 `{value}` 年，长期客户更倾向标准化服务方案 | —（非关键特征，Customer 版可省略） |
| `customer_vertical` | Vertical `{value}` 的保修偏好偏高档，均值 `{avg_tier}` | 您所在行业的客户普遍重视服务响应速度 |

**负向特征（仅 Internal）**：

| 特征名 | Internal 表述模板 |
|--------|-----------------|
| `customer_segment`（负） | `{value}` 客户平均保修等级 `{avg_tier}`，低于推荐方案 1+ 档 |
| `customer_is_new` | 新客户，历史数据不足，推荐置信度受影响 |

---

## 3. 地理位置维度（Geography）

| 特征名 | Internal 表述模板 | Customer 表述模板 |
|--------|-----------------|-----------------|
| `country` | `{value}` 市场此类保修采纳率 `{rate}%`，与全球均值 `{global_rate}%` 对比 | 在 `{value}` 地区，大多数企业客户选择此服务级别 |
| `region` | `{value}` 区域保修等级偏好 `{avg_tier}` | `{value}` 地区的商业环境适合此保障方案 |
| `geo_service_availability` | 该服务在 `{value}` 可用（通过业务规则校验） | —（可用性不向客户暴露为"推荐理由"） |
| `country_regulation_complexity` | `{value}` 市场监管复杂度 `{level}`，高复杂度市场倾向更全面的合规保障 | 考虑到您所在市场的监管要求，全面保障有助于合规管理 |

**负向特征（仅 Internal）**：

| 特征名 | Internal 表述模板 |
|--------|-----------------|
| `country`（负） | `{value}` 市场 Premier 采纳率 `{rate}%`，低于全球平均 `{global_rate}%` |
| `geo_service_restriction` | 部分高级服务在 `{value}` 受限，推荐方案已排除不可选项 |

---

## 4. 交易维度（Deal）

| 特征名 | Internal 表述模板 | Customer 表述模板 |
|--------|-----------------|-----------------|
| `hardware_value_band` | 硬件价值处于 `{value}` 区间，该区间此类保修采纳率 `{rate}%` | 您的硬件投资规模较大，相应级别的服务保障有助于保护资产 |
| `hardware_value_absolute` | 硬件价值 `${value}`，高于/低于同 segment 中位数 `${median}` | —（不展示绝对金额） |
| `contract_type` | `{value}` 合同类型，该类型的保修等级倾向 `{direction}` | —（不展示合同类型分析） |
| `deal_size_category` | 交易规模 `{value}`（`{size}`），大额交易倾向更完整保障 | 根据您的项目规模，我们建议匹配完整的服务覆盖 |
| `channel_type` | `{value}` 渠道，该渠道保修搭配偏好 `{tier}` | —（渠道信息不向客户展示） |
| `bid_type` | `{value}` 类报价，同类 bid 的 Premier 采纳率 `{rate}%` | —（报价类型不向客户展示） |

**负向特征（仅 Internal）**：

| 特征名 | Internal 表述模板 |
|--------|-----------------|
| `contract_type`（负） | `{value}` 合同对该等级保修有轻微负向影响（`{shap}`），但不改变排名 |
| `hardware_value_band`（负） | 硬件价值 `{value}`，低于推荐方案通常匹配的区间 |

---

## 5. 历史模式维度（Historical Patterns）

| 特征名 | Internal 表述模板 | Customer 表述模板 |
|--------|-----------------|-----------------|
| `historical_attach_rate` | 同类 bid 中该服务的历史采纳率 `{rate}%` | —（不展示内部历史数据） |
| `similar_customer_behavior` | 同 segment `{seg}` + 同 geo `{geo}` 客户群中 `{rate}%` 选择了此保修 | 与您类似的企业客户普遍选择此方案 |
| `product_service_pair_freq` | `{hw}` + `{svc}` 组合在历史数据中出现频率 `{freq}`，关联度等级 `{level}` | —（不展示内部频次数据） |
| `recent_trend_direction` | 近 `{months}` 个月该服务的采纳趋势 `{direction}`（`{pct}` 个百分点） | 近期越来越多客户选择更全面的保障方案 |
| `seasonal_factor` | 季度因子 `{quarter}` 影响 `{direction}`（`{magnitude}`），当前为 `{value}` | —（不展示季节性分析） |

---

## 6. 特征工程衍生维度

| 特征名 | Internal 表述模板 | Customer 表述模板 |
|--------|-----------------|-----------------|
| `sparse_encoder_cluster` | 稀疏编码器将当前 bid 映射到 cluster `{id}`，该 cluster 保修偏好 `{preference}` | —（不暴露编码器内部逻辑） |
| `feature_interaction_score` | `{feat_a}` × `{feat_b}` 交互项贡献 `{shap}` — 表明 `{explanation}` | —（不暴露特征交互） |
| `data_freshness_weight` | 数据新鲜度权重 `{weight}`（最后一次同类交易距今 `{days}` 天） | —（不暴露数据时效性） |

---

## 7. 召回来源标识

| 来源 | Internal 表述 | Customer 表述 |
|------|-------------|-------------|
| `Engine I`（冷启动） | 冷启动模式 — 基于硬件配置关联规则（无历史行为数据） | 根据您的硬件配置匹配了适配的基础服务 |
| `Engine II`（热启动） | 热启动模式 — 基于同 segment 历史偏好 + 产品关联规则 | 参考了大量类似配置客户的实际选择 |

---

## 8. 业务规则过滤

| 规则 | Internal 表述 | Customer 表述 |
|------|-------------|-------------|
| `geo_availability: pass` | 该服务在目标国家可售 ✓ | — |
| `geo_availability: fail` | 该服务在目标国家不可售 ✗（已过滤） | — |
| `eol_check: pass` | 相关硬件未进入 EOL ✓ | — |
| `eol_check: fail` | 相关硬件已 EOL，对应服务已排除 ✗ | — |
| `compliance_check: pass` | 合规校验通过 ✓ | — |
| `baseline_calibration` | 基线校准已应用（最低展示 `{n}` 个方案） | — |

---

## 9. Add-on 推荐

| Add-on 类型 | Internal 表述 | Customer 表述 |
|------------|-------------|-------------|
| `Installation` | Installation (`{option}`)：概率 `{prob}%`，基于 `{rate}%` 同类客户选择 | 标准工作时间上门安装服务，确保设备快速就绪 |
| `KYD` | Keep Your Drive (`{term}`)：概率 `{prob}%`，基于同机型共现统计 | `{term}` 硬盘保留服务，数据安全更有保障 |
| `CO2 Offset` | CO₂ Offset：概率 `{prob}%`，基于 `{rate}%` 同 segment 选择 | 碳排放抵消服务，助力您的可持续发展目标 |
| `CSR` | CSR (`{sla}`)：概率 `{prob}%`，基于 `{rate}%` 同机型搭配 | `{sla}` 客户可更换部件服务，减少停机时间 |

---

## 补充说明

### 待补充特征

以上覆盖了 6 个维度的代表性特征。完整的 50+ 特征映射表需要：

1. **实际特征名清单**：从 XGBoost 模型的 feature_names 获取
2. **SHAP 值分布**：了解每个特征的典型贡献大小和方向
3. **业务含义注解**：由产品/PM 团队确认每个特征的业务含义

### 维护流程

```
1. 模型训练产出新特征 → 
2. 特征名加入本表 → 
3. 内部 PM 填写 Internal/Customer 表述 → 
4. 审查措辞（避免歧义/过度承诺） → 
5. 上线到推理 Pipeline
```

---

*Next: Prompt 工程规范*
