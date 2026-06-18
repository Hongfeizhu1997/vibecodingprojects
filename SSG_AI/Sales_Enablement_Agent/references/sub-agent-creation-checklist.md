# Sub-Agent 创建清单

> 创建：2026-06-18 | 源自：Sales Enablement Agent 架构讨论
> 用途：创建新 Sub-Agent 时的操作检查清单。基于 DeerFlow (Vetraflow) 框架。

---

## 总览

```
Sub-Agent = {
    System Prompt（"我是谁"）
    Tool Bindings（"能碰什么系统"）
    Skill Bindings（"会哪些操作流程"）
    RAG Scope（"能查哪些知识"）
    Memory Scope（"能记住什么"）
}
```

最终产出：一个 DeerFlow YAML 配置文件（`/configs/agents/{name}.yaml`）。

---

## 步骤 1：System Prompt

**写一段文本定义：**

- [ ] 我是谁（角色定位，一句话）
- [ ] 我能做什么（能力列表，每项一行）
- [ ] 我不能做什么（硬边界，必须写清楚）
- [ ] 我如何回答（语气、格式、拒绝话术）

**关键原则**：
- 边界必须写"不能做什么"——LLM 默认倾向是帮忙，不写禁止它会尝试越界
- 写标准拒绝话术，确保行为一致
- Tone 指令简短但必要

---

## 步骤 2：Tool Bindings

**列出可调用的系统 API（白名单 + 黑名单）：**

- [ ] 每个 Tool 声明 `description`（给 LLM 看——帮助它判断何时调用）
- [ ] 每个 Tool 声明 `permission`（read_only / approval_required）
- [ ] 标出明确禁止的系统（"不可调 CPM"比"没列 CPM"更安全）
- [ ] 设置 `timeout` 和 `retry`

**关键原则**：
- `description` 不是给人看的——LLM 据此决定"现在该调这个 tool"
- 只读 Tool 和写入 Tool 必须分开标注
- 显式黑名单比隐式白名单更安全

---

## 步骤 3：Skill Bindings

**加载可复用的操作流程模板：**

- [ ] 列出需要加载的 Skill 名称
- [ ] 每个 Skill 必须已经声明依赖（参见 `skill-dependency-spec.md`）
- [ ] 校验：Agent 的 Tool 白名单 + RAG Scope 是否满足 Skill 的 `requires`
- [ ] 未满足 → 拒绝加载或降级处理

**关键原则**：
- Skill 可跨 Agent 复用，但必须通过依赖校验
- 优先拆成"通用核心 Skill" + "Agent 专属扩展 Skill"
- 依赖不满足在**配置时**就报错，不等运行时

---

## 步骤 4：RAG Scope

**划定可检索的知识域：**

- [ ] 列出允许查询的 RAG 索引（白名单）
- [ ] 明确排除的索引（如有）
- [ ] 设置 `top_k`（单次检索返回条数）
- [ ] 设置 `score_threshold`（最低相关度）

**关键原则**：
- RAG Scope 比 Tool 权限更容易被忽略，但静默失败的后果更严重
- 按"最小必要原则"划定——Agent 只需要自己领域相关的知识
- `approval_rules` 建议所有 Agent 共享

---

## 步骤 5：Memory Scope

**定义记忆范围：**

- [ ] Short-term：单次会话记什么（如 `current_pn_id`）
- [ ] Long-term：跨会话记什么（如 `frequently_queried_pns`）
- [ ] Domain：团队共享记什么（如 `common_duplicate_patterns`）

**关键原则**：
- Short-term 只记当前必要的上下文——记太多导致 prompt 膨胀
- Long-term 记"不因时间变化的偏好"——不是任务历史
- Domain 记团队模式——跨用户共享

---

## 产出模板

```yaml
# DeerFlow Agent Config: /configs/agents/{agent_name}.yaml

name: {agent_name}
version: 1.0
type: sub              # sub or master

# 步骤 1
system_prompt: |
  You are the [role] for SSG GPS.
  ...
  
# 步骤 2
tools:
  - tool_name_1
  - tool_name_2
  # 每个 tool 的完整定义在 tools/ 目录下

# 步骤 3
skills:
  - skill_name_1
  - skill_name_2

# 步骤 4
rag_scope:
  indexes:
    - index_name_1
    - index_name_2
  top_k: 5
  score_threshold: 0.7

# 步骤 5
memory:
  short_term:
    fields: [field_1, field_2]
  long_term:
    fields: [field_1, field_2]
  domain:
    fields: [field_1, field_2]
```

---

## 校验清单（交付前）

- [ ] System Prompt 是否写了硬边界和拒绝话术
- [ ] Tool 白名单是否包含不应该有的写入 Tool
- [ ] Skill 依赖是否全部通过校验
- [ ] RAG Scope 是否包含不应该有的索引
- [ ] Memory 字段是否过多（超过 5 个 field 警惕）
- [ ] YAML 语法是否正确
