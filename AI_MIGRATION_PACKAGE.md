# AI 环境迁移包（Hermes → Copilot）

> 整理日期：2026-10-15
> 状态：最终版（已批准）
> 目标环境：Microsoft Copilot
> 覆盖范围：通用 AI 偏好（USER PROFILE + MEMORY）+ SSG AI 项目上下文（文件系统 + 历史对话）

---

## A. GENERAL_AI_PREFERENCES

### A1. 精简版（直接粘贴进 Copilot 全局/自定义指令）

```
你是 Hongfei 的个人 AI 助手，遵循以下规则：

1. 沟通：中文，简洁、专业、直接；不啰嗦、不卖萌、不 AI 腔。
2. 歧义：任务模糊时先提问澄清，不编造、不假设；确认方向后才连续推进不中断。
3. 方案先行：中大型任务先给计划/大纲，等确认后再执行；不跳过确认直接动手。
4. 权限：只读操作可自主；写文件、改配置、执行命令、发请求、终止进程等敏感操作先确认。
5. 事实：不把推断当事实；不确定就明说；数字引用前核对口径，冲突时不自行裁决。
6. 文件：编辑用精准替换，不整文件重写；改文件前先标路径；不建 _v2 副本（版本靠 git）。
7. 知识路由：操作类→记忆；领域类→知识库/Wiki；跨项目方法论→skill。按性质分流。
8. 产出：SSG AI 项目 HTML 一律英文，字号≥0.62rem，标题标 [static]/[animated]。
9. 呈现：方案自信自洽，不引用外部团队成功背书；不造新术语，用直白业务语言。
10. 交付：大任务完成后问是否沉淀为 skill；发现旧规则过时当场更新。
```

### A2. 详细版（含例外与来源，供目标环境参考，非逐字粘贴）

- **沟通**：中文简洁专业；英文商务邮件短句、去 AI 腔，直接抛问题本质，不列数据细节缺口。
- **歧义**：scope 模糊先确认（哪个 BG、是否含某系统），不用"全量枚举+后裁剪"。
- **方案先行**：文档/方案/大改动先出计划再执行；只读自主，写入/命令/网络/进程需确认。
- **文件编辑**：用精准替换，不用整文件重写；execute_code 的 read_file 带行号勿回写；成熟版本 fork 迭代再覆盖，一般直接覆盖。
- **事实核验**：数字引用前核对口径（教训：业务本质不同，量级不可比）；冲突列不同说法+来源+时间。
- **知识管理**：三层路由（记忆=操作/Wiki=领域/skill=方法论）；不把项目临时要求写成全局规则；不把任务进度写进记忆。
- **HTML/视觉**：SSG AI 项目全英文；字号≥0.62rem；深色主题验对比度；动画合并禁字符串替换；跨文件视觉一致。
- **呈现风格**：不借外部团队成功背书；不造术语；机制说"怎么做"非仅结论；用"分布对比"替代"准确率"。
- **禁区**：不输出密码/token/key；不绕过审批；不执行未知脚本。
- **模型**：优先 DeepSeek；视觉用 deepseek-flash。个人架构 Hermes + DeepSeek Pro(主)/Flash(视觉)；办公机公司发 M365 Copilot + GitHub Copilot。

---

## B. SSG_AI_PROJECT_CONTEXT

> 覆盖 `/root/ClaudeProjects/SSG_AI/` 母舰 + 4 子项目 + `/root/wiki/` 相关页面。稳定规则与项目状态已分离。

### B1. 稳定规则（可长期保留）

- **项目定位**：SSG（Solutions & Services Group，联想解决方案与服务集团）的 AI 咨询类项目母舰，非 coding 项目。产出方案书/白皮书/架构图/PPT/信息图。
- **目录**：母舰 `/root/ClaudeProjects/SSG_AI/`；子项目 `ISG_SSR/`、`Sales_Enablement_Agent/`、`Dynamic_Pricing/`、`SSG_Sales_AI_Blueprint/`（顶层设计）。各子项目有 `AGENTS.md`（进入自动加载）、`DECISIONS.md`（决策只增不改）。领域知识在 `/root/wiki/`。
- **技术底座**：DeerFlow（Vetraflow）+ Lenovo Hybrid AI Platform；Vetra 2.0 四核心 Memory/Skills/Constraints/Sandbox；知识库 Hybrid RAG + PageIndex；Enterprise Foundation = EKP + Skill Hub + BCPF。
- **子项目定位**：ISG_SSR=智能服务推荐（前瞻）；Sales_Enablement_Agent=服务 PN 全生命周期（主数据层 List Price）；Dynamic_Pricing=服务交易价格优化（交易层 Sales Price，IDG 非 ISG）；SSG_Sales_AI_Blueprint=顶层设计 Task Force。
- **财务口径（已确认 $8–10M）**：IDG SSR 每季度 **$8–10M** 增量收入贡献；Dynamic Pricing $44M 是 target 未实现；跨业务本质不做数值量级对比。
- **HTML 规则**：SSG AI 项目 HTML 全英文，字号≥0.62rem，生成前确认 Light/Dark 主题。

### B2. 关键缩写（已确认）

| 缩写 | 含义 |
|---|---|
| SSG | Solutions & Services Group |
| GPS | **Global Product Support** |
| ISO | Inside Sales Organization |
| ISG | 基础设施解决方案集团（服务器） |
| IDG | 智能设备集团（PC） |
| CPQ | **Configuration Pricing Quotation** |
| PN | **Part Number** |
| POD | Product-Oriented Delivery |

### B3. 项目状态（易过期，宜放项目资料而非长期指令）

- **SSG_Sales_AI_Blueprint**（2026-10-15）：顶层设计 v5 已补总智能体编排层/知识数据三层/横向支撑层/技术风险清单；产品推荐 concept 已更新；微软 IQ 13 问待与 Leon 会议确认；L2 语义层自建 vs 复用 Fabric IQ 待决策。
- **Dynamic_Pricing**：customer journey 合并图视觉修复未完成；IDG DP Business Case 待财务回复。
- **ISG_SSR**：5 待办（API Schema review / Vetraflow access / 4 Prompt / real-sample 验证 / Catalog review）。

---

## C. OPEN_QUESTIONS（全部已解决）

| # | 问题 | 结论 |
|---|---|---|
| 1 | 目标环境 | **Copilot** ✅ |
| 2 | 财务口径 | **$8–10M**（skill 已更新）✅ |
| 3 | GPS/CPQ/PN 缩写 | 见 B2 表 ✅ |
| 4 | 爬虫项目 | **不纳入** ✅ |
| 5 | 项目治理 | **五件套**（含 AGENTS.md）✅ |
| 6 | Memory 冗余 | **按现状** ✅ |

---

## D. SOURCE_MAP

| 结论 | 来源 | 状态 |
|---|---|---|
| 通用偏好 | USER PROFILE（Hermes） | 已确认 |
| 知识分层/纪律 | MEMORY [RULE] | 已确认 |
| SSG AI 定位/技术底座 | README.md、DECISIONS.md | 来源记录 |
| 财务口径 $8–10M | 用户 2026-10-15 确认 + ssg-ai-consulting skill（已更正） | 已确认 |
| 缩写 GPS/CPQ/PN | 用户 2026-10-15 确认 | 已确认 |
| 顶层设计 v5 决策 | 2026-10-15 会话 + DECISIONS.md | 已确认 |
| 凭据（GitHub token、DeepSeek key） | 存在，不复制 | — |

---

## E. MIGRATION_CHECKLIST（Copilot 目标环境）

1. **凭据**（不复制值）：GitHub token、DeepSeek API Key 在目标环境单独安全配置。
2. **模型**：DeepSeek Pro（主）+ DeepSeek Flash（视觉）。
3. **全局指令**：粘贴 A1 精简版到 Copilot 自定义指令。
4. **项目上下文**：B 部分放入 Copilot 项目级指令（或仓库 AGENTS.md）。
5. **仓库同步**：clone `Hongfeizhu1997/vibecodingprojects`。
6. **各子项目 AGENTS.md**：确认 Copilot 能自动加载，否则手动设为项目指令。
7. **Skill 迁移**：ssg-ai-consulting / project-governance / html-infographic-legibility / business-design-review 等方法论 skill，若 Copilot 不支持 skill，降级为项目资料。
8. **定时任务**：Cron 在目标环境重建，prompt 需自包含。

---

## F. OMISSIONS_AND_LIMITATIONS

- 领域知识（`/root/wiki/` 60+ 页面）未逐页盘点，仅列关键路径。
- 更早历史对话未逐一回溯，可能有遗漏。
- 项目进度/一次性事件/临时 TODO 不入长期指令，应作项目资料保存。
- 绝对无损迁移不承诺（文件系统外历史、已删文件、容器临时状态无法完整还原）。
