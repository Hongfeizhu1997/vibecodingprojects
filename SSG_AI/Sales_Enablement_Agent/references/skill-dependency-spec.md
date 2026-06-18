# Skill 依赖声明规范

> 创建：2026-06-18 | 源自：Sales Enablement Agent 架构讨论
> 问题：Skill 内引用 Tool/RAG，目标 Agent 无权限 → 静默失败

---

## 核心规则

**每个 Skill 必须显式声明依赖。绑定到 Sub-Agent 时自动校验，依赖不满足 → 拒绝加载。**

---

## 字段定义

```yaml
requires:
  tools:          # 必需 Tool 列表。缺失 → 拒绝加载
    - tool_name
  rag_indexes:    # 必需 RAG 索引列表。缺失 → 拒绝加载
    - index_name
  optional:
    tools:        # 可选 Tool。有更好，没有降级
      - tool_name
    rag_indexes:  # 可选 RAG 索引。有更好，没有跳过
      - index_name
```

---

## 示例

```yaml
name: skill_odt_change_impact_analysis
version: 1.0

requires:
  tools:
    - odt_query_pn_attributes
    - concord_query_booking_by_pn
  rag_indexes:
    - odt_attribute_fields
    - risk_mapping
  optional:
    tools:
      - cpm_read_sales_cost
    rag_indexes:
      - approval_rules

steps: |
  1. PARSE user input...
  2. Call odt_query_pn_attributes(pn_id)
  3. Call concord_query_booking_by_pn(pn_id)
  4. Call query_rag("warranty term change impact mapping")
     → requires risk_mapping index
  5. If cpm_read_sales_cost available: enrich with cost data
     If not: skip cost section
  6. FORMAT result...
```

---

## 判定逻辑

| 情况 | 行为 |
|------|------|
| `requires.tools` 全部在 Agent Tool 白名单 | ✅ 加载 |
| `requires.tools` 任一缺失 | ❌ 拒绝，报冲突 |
| `requires.rag_indexes` 全部在 Agent RAG Scope | ✅ 加载 |
| `requires.rag_indexes` 任一缺失 | ❌ 拒绝，报冲突 |
| `optional.tools` 缺失 | ⚠️ 加载但降级 |
| `optional.rag_indexes` 缺失 | ⚠️ 加载但跳过该步骤 |

---

## Skill 复用策略

当 Skill 的部分依赖不是所有 Agent 都满足时：

| 策略 | 做法 | 适用场景 |
|------|------|---------|
| 硬依赖 | 声明 `requires`，校验不通过拒绝加载 | Skill 核心逻辑离了它走不通 |
| 可选依赖 | 声明 `optional`，缺失时降级 | "有更好，没有也能给基本回答" |
| 拆分 Skill | 通用核心 + Agent 专属扩展（`extends`） | 核心流程通用，某步需特定系统 |

### 拆分示例

```yaml
# 通用 Skill（所有 Agent 可加载）
name: skill_change_impact_core
requires:
  rag_indexes: [risk_mapping]
steps: |
  1. Parse change details
  2. Map change type to impact dimensions (RAG)
  3. Classify risk level
  4. Format output card

# PN Agent 专属 Skill（继承核心 + Booking 查询）
name: skill_odt_change_with_booking
extends: skill_change_impact_core
requires:
  tools: [odt_query_pn_attributes, concord_query_booking_by_pn]
steps: |
  1. Execute skill_change_impact_core
  2. Before Step 4, insert:
     Query ODT → Query Concord → Add Booking Impact section
```

---

## RAG 静默失败警告

Tool 缺失 → Agent 直接报错（易发现）。
**RAG 索引缺失 → query_rag 正常返回但结果不相关**（静默失败）。

因此 RAG 依赖校验比 Tool 更重要——必须做，不能跳过。
