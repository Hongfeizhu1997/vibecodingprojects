# ISG SSR 能力技能化 — 可行性探索

> 创建：2026-06-23 | 触发：将小模型推荐 + 大模型可解释性打包为可发布 Skill
> 问题：能否将 ISG SSR 的核心能力包装成一个 Skill，供联想内部所有 AI Agent 调用？

---

## 1. 当前 ISG SSR 能力栈

```
                    ┌──────────────────────────┐
                    │  Stage 7: LLM 解释生成    │  ← 大模型：ChatGPT via Vetraflow
                    │  SHAP → 业务语言 × 4套    │
                    ├──────────────────────────┤
                    │  Stage 3: XGBoost 排序    │  ← 小模型：训练好的 ML Pipeline
                    │  特征嵌入 → 打分 → SHAP   │
                    ├──────────────────────────┤
                    │  Stage 1-2: 特征+召回     │
                    │  Stage 4-5: 规则+Add-on   │
                    └──────────────────────────┘
```

**核心价值**：给定一个 Bid（客户/硬件/国家/合同上下文），输出：
- 排序后的服务产品推荐（概率 + 置信度）
- 每个推荐的 SHAP 特征贡献（可解释性）
- LLM 生成的双受众自然语言解释（内部版 + 客户版，× 中英文）

---

## 2. "技能化" 意味着什么

在 Lenovo 企业 AI 生态中，Skill = 一个 Agent 可发现、可加载、可调用的能力模块。

### 2.1 三类 Skill 形态

| 形态 | 复杂度 | 示例 | ISG SSR 适合？ |
|------|--------|------|:---:|
| **Prompt Skill** | 低 | 模板化提示词、Few-shot 示例 | ❌ 不只是 Prompt |
| **Tool Skill** | 中 | API 封装 + 输入校验 + 降级逻辑 | ⚠️ 部分适合 |
| **Capability Skill** | 高 | 完整推理 Pipeline + 自有模型 + 知识库 | ✅ 最接近 |

ISG SSR 不是 Prompt 模板，也不是简单的 API 调用——它有**自有模型**（XGBoost）、**自有数据 Pipeline**（特征工程）、**自有推理逻辑**（SHAP → LLM 翻译）。它更像一个**微服务能力**。

### 2.2 技能化的核心问题

**问题不在"能不能"——在"怎么做"和"代价是什么"。**

技能化的本质是将现在的「项目内嵌能力」提升为「平台级可复用能力」，需要回答：

1. **接口契约**：别的 Agent 怎么调用？输入什么、输出什么？
2. **模型部署**：XGBoost 模型跑在哪？谁负责推理？
3. **LLM 依赖**：Stage 7 的 ChatGPT 调用是 Skill 内部的还是外部组合的？
4. **发现机制**：别的 Agent 怎么知道有这个 Skill？
5. **权限控制**：谁能调、调多少次？
6. **版本管理**：模型更新后 Skill 怎么升级？已有调用方怎么迁移？

---

## 3. 架构方案对比

### 方案 A：嵌入式 Skill（模型 + 逻辑一体化）

```
Agent 加载 Skill → Skill 内置 XGBoost 模型 + SHAP 逻辑
                  → 调用方传入 Bid JSON
                  → Skill 本地推理 + 调用 LLM 生成解释
                  → 返回完整推荐结果
```

**优点**：自包含、无网络依赖、低延迟
**缺点**：
- XGBoost 模型文件（含特征工程逻辑）体积大，不适合每个 Agent 都加载
- 模型更新需要所有调用方重新加载 Skill
- Agent 运行环境可能无 ML 运行时（无 xgboost/pandas/sklearn）
- **这更接近"分发一个 Docker 镜像"而非"加载一个 Skill"**

### 方案 B：代理式 Skill（Skill = 接口封装，模型远程推理）

```
Agent 加载 Skill → Skill 提供标准接口
                  → 调用方传入 Bid JSON
                  → Skill 将请求转发到模型推理服务（自建 API）
                  → 推理服务跑 XGBoost → 返回推荐 + SHAP
                  → Skill 调用 LLM 生成解释（或推理服务已完成）
                  → 返回完整结果给调用方
```

**优点**：
- Skill 轻量（只是一层接口封装）
- 模型独立部署、独立升级
- Agent 无需 ML 运行时
- 模型服务可做统一的监控、限流、A/B 测试

**缺点**：
- 需要单独部署模型推理服务
- 增加一次网络调用延迟
- 模型服务成为单点依赖

### 方案 C：分体式 Skill（推荐 Skill + 解释 Skill 独立）

```
┌──────────────────────────────────────────────────┐
│              Skill Hub (Lenovo 企业平台)           │
│                                                   │
│  ┌─────────────────┐    ┌──────────────────────┐  │
│  │ ServiceRecSkill  │    │ LLMExplainSkill      │  │
│  │ (小模型推荐)      │←──→│ (大模型可解释性)       │  │
│  │                  │    │                      │  │
│  │ Bid → Recs+SHAP  │    │ Recs+SHAP → 解释文本  │  │
│  └─────────────────┘    └──────────────────────┘  │
│         ↓                        ↓                │
│  ┌──────────────────────────────────────────┐     │
│  │    XGBoost Inference Service (独立部署)    │     │
│  └──────────────────────────────────────────┘     │
└──────────────────────────────────────────────────┘
```

**优点**：
- 两个 Skill 可独立使用或组合
- LLM 解释逻辑可复用于其他推荐场景（不只是 ISG）
- 符合单一职责原则

**缺点**：
- 两个 Skill 的接口耦合（LLMExplainSkill 依赖 ServiceRecSkill 的输出去格式）
- 增加了组合复杂度

---

## 4. 推荐方案：B（代理式）为起点，渐进到 C

### 4.1 为什么是 B

| 因素 | 判断 |
|------|------|
| 技能化速度 | B 最快——只需定义接口 + 部署模型服务，Skill 本体是轻量封装 |
| 模型部署 | 模型服务独立部署是迟早的事（不技能化也要做） |
| Agent 兼容性 | B 不要求 Agent 有 ML 依赖，任何 Agent 都能调 |
| 升级灵活性 | 模型更新只改推理服务，Skill 接口不变则下游无感知 |
| 与 Lenovo Skill Hub 对齐 | Skill Hub 的 Skill 本质是"能力描述 + 调用接口"，B 最贴合 |

### 4.2 渐进路径

```
Phase 1 (现在):   ISG SSR 项目内嵌能力（当前状态）
Phase 2:          部署 XGBoost 推理服务 + 创建 ServiceRecSkill（方案 B）
Phase 3:          从 ServiceRecSkill 中拆出 LLMExplainSkill（方案 C）
                  → LLMExplainSkill 可被其他推荐场景复用
```

---

## 5. 接口契约设计（ServiceRecSkill）

### 5.1 输入

```json
{
  "bid_id": "US-NA-2026-06421",
  "context": {
    "country": "US",
    "customer_segment": "Enterprise",
    "industry": "Finance",
    "hardware_config": "SR650 V3",
    "hardware_value_band": "high",
    "contract_type": "new_bid",
    "vertical": "FSI"
  },
  "options": {
    "language": ["en", "zh"],
    "audience": ["internal", "customer"],
    "top_k": 3,
    "include_addons": true,
    "include_explanations": true
  }
}
```

### 5.2 输出

```json
{
  "bid_id": "US-NA-2026-06421",
  "model_version": "xgboost-v2.3.1-20260601",
  "recommendations": [
    {
      "rank": 1,
      "service_type": "Premier",
      "warranty_term": "3Y",
      "warranty_sla": "24x7 4hr",
      "probability": 0.72,
      "confidence": "medium",
      "shap_drivers": [
        {"feature": "customer_segment", "impact": "+0.18", "direction": "push_up"},
        {"feature": "hardware_value",   "impact": "+0.14", "direction": "push_up"}
      ],
      "explanations": {
        "internal_en": "Recommendation primarily driven by...",
        "internal_zh": "推荐主要基于客户属于企业级细分...",
        "customer_en": "Based on your enterprise profile and hardware selection...",
        "customer_zh": "基于您的企业规模及硬件配置..."
      }
    }
  ],
  "addons": [...]
}
```

### 5.3 关键设计决策

| 决策 | 结论 | 理由 |
|------|------|------|
| LLM 解释在 Skill 内还是外 | **Skill 内** | 调用方不应关心"解释是怎么生成的"，只需拿到结果 |
| 多语言/多受众 | **Skill 内全量生成** | 一次调用生成全部版本，调用方按需取用 |
| 模型版本暴露 | **暴露** | 调用方需要知道哪个模型版本产出的结果（可审计） |
| 降级策略 | **LLM 不可用时返回模板化解释** | SHAP 数据始终可用，降级到 `feature_name: shap_value` 模板 |

---

## 6. 部署架构

```
                    调用方 Agent
                   (Sales / Pricing / ...)
                         │
                   加载 Skill
                         │
              ┌──────────┴──────────┐
              │   ServiceRecSkill    │  ← 轻量接口层（Prompt + 校验）
              │   (Skill Hub 发布)    │
              └──────────┬──────────┘
                         │ REST/gRPC
              ┌──────────┴──────────┐
              │  ISG SSR Inference   │  ← 独立推理服务
              │  Service             │
              │  ├── XGBoost Model   │
              │  ├── SHAP Engine     │
              │  ├── Feature Pipeline│
              │  └── LLM Connector───┼──→ Vetraflow → ChatGPT
              └─────────────────────┘
```

### 6.1 推理服务部署选项

| 选项 | 适用 | 备注 |
|------|------|------|
| Lenovo Hybrid AI Platform | ✅ 首选 | 内部统一 AI 基础设施，天然支持模型部署 |
| DeerFlow/Vetraflow Sandbox | ⚠️ 备选 | Skill 可直接跑在 DeerFlow Sandbox |
| 独立容器化部署 | ✅ 可行 | Docker + FastAPI，最灵活 |

---

## 7. 与 Lenovo Skill Hub 的对齐

```
Lenovo Skill Hub (企业级 Skill 目录)
│
├── ServiceRecSkill          ← ISG SSR 能力技能化
│   ├── 描述：ISG 服务产品智能推荐 + 可解释性
│   ├── 输入：Bid 上下文
│   ├── 输出：排序推荐 + SHAP 解释 + LLM 自然语言
│   ├── 依赖：ISG SSR Inference Service, Vetraflow
│   └── 权限：需 ISG 服务推荐权限
│
├── Sales Enablement Skills   ← SSG GPS 生命周期
├── Pricing Skills            ← 动态定价
└── ...其他 Skills
```

**关键对齐点**：
- Skill Hub 作为发现层——Agent 通过 Skill Hub 知道有这个能力
- Skill 加载后通过 DeerFlow Runtime 执行
- 模型推理通过 Hybrid AI Platform 的 Model Serving 能力

---

## 8. 边界拓展：技能化后的新场景

一旦成为平台级 Skill，以下场景全部解锁：

| 新场景 | 调用方 Agent | 输入来源 |
|--------|-------------|---------|
| GPS PM 做 PN 时自动获取服务推荐 | Sales Enablement Agent | PN 创建时的 Bid 上下文 |
| 定价 Agent 参考推荐调整服务定价 | Pricing Agent | 定价计算中的 Bid 数据 |
| 客户自助 Portal 查看推荐 | Customer-facing Agent | 客户登录后的 profile |
| 批量 Bid 分析（季度复盘） | Analytics Agent | 历史 Bid 数据批量传入 |
| 新市场冷启动推荐 | Market Expansion Agent | 新国家/地区的市场数据 |

**技能化前**：ISG SSR 只服务一个项目、一个场景
**技能化后**：任何 Agent 在需要"服务产品推荐 + 解释"时都能调用

---

## 9. 风险与开放问题

| # | 风险/问题 | 严重程度 | 缓解措施 |
|---|----------|:--------:|---------|
| 1 | XGBoost 模型是否对所有场景通用 | 🔴 高 | 需验证模型在新市场/新客户段的表现，可能需要分区域训练 |
| 2 | LLM 解释质量是否稳定 | 🟡 中 | Few-shot + 校验 + 降级模板已设计 |
| 3 | 推理服务 SLA 要求 | 🟡 中 | 其他 Agent 可能是实时场景，需定义响应时间承诺 |
| 4 | Skill 权限控制粒度 | 🟡 中 | 需要与 Skill Hub 团队确认权限模型 |
| 5 | 模型更新后的向后兼容 | 🟢 低 | 输出 Schema 版本化，旧版保留过渡期 |
| 6 | 特征数据从哪里来 | 🟡 中 | 当前依赖 ISG 的 Data Pool，技能化后调用方需传入完整 Bid 上下文 |

### 9.1 最大不确定性

**特征数据的可获得性**。当前模型依赖 300+ 字段的 Data Pool → 50+ 特征。如果调用方 Agent 拿不到完整的 Bid 数据（比如客户自助 Portal 只有部分信息），模型推理质量会下降。

**需要定义"最小可调用输入"**：哪些字段是必需的、哪些字段缺失时用默认值填充。

---

## 10. 建议的行动计划

```
Week 1-2:  确认推理服务部署方案（Hybrid AI Platform vs 独立部署）
            输出：技术选型文档 + 部署 POC

Week 3-4:  定义 ServiceRecSkill 正式接口契约（输入/输出 Schema 定稿）
            输出：OpenAPI/Skill Manifest 文件

Week 5-6:  实现 Skill 封装 + 推理服务对接
            输出：可用的 ServiceRecSkill v0.1

Week 7:    内部 Dogfood（选 1-2 个 Agent 场景试调用）
            输出：反馈 + 改进清单

Week 8:    Skill Hub 发布 v1.0 + 文档
```

---

## 11. Bottom Line

**可行，且价值巨大。** ISG SSR 不是只能服务于自己项目的封闭能力——小模型推荐 + 大模型解释是一个通用模式，任何场景只要涉及"需要推荐 + 需要解释为什么推荐"都可以复用。

技能化不是技术难题，而是**架构升级决策**——从"项目内嵌能力"升级为"平台级可复用能力"。最大工作不在代码，在：
1. 模型推理服务的独立部署
2. 接口契约的标准化
3. 特征数据可获得性的验证

**推荐先做 Phase 2（方案 B），快速跑通一个调用链，再考虑拆分为方案 C。**
