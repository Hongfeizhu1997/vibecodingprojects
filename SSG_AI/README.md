# SSG AI — 传统业务 × AI 咨询项目

> 积累传统业务经验 · 探索行业最佳 AI 实践 · 形成可交付的咨询输出

---

## 项目定位

这不是一个 coding 项目，而是一个**咨询类项目**。目标是：

1. **积累** — 系统化收集传统行业（如制造、零售、金融、服务等）的业务经验、痛点和流程
2. **探索** — 持续追踪 AI 技术在各行业的最佳实践案例，评估其适用性和效果
3. **输出** — 形成方案书、白皮书、PPT 演示、信息图、培训材料等咨询交付物

---

## Hermes Agent 咨询能力全览

以下按咨询项目的工作流阶段，梳理所有可用技能。

### 一、研究与情报收集

| 技能 | 用途 | 典型场景 |
|------|------|---------|
| `arxiv` | 学术论文搜索（arXiv + Semantic Scholar） | 追踪 AI 前沿研究、引文分析、文献综述 |
| `blogwatcher` | RSS/Blog 订阅监控 | 追踪行业博客、竞品动态、技术趋势 |
| `web-scraping` | 网页数据抓取（完整工作流） | 行业数据收集、竞品价格监控、论坛舆情 |
| `polymarket` | 预测市场数据查询 | 事件概率分析、市场情绪参考 |
| `ocr-and-documents` | PDF/扫描件文本提取 | 处理行业报告、白皮书、扫描文档 |
| `youtube-content` | YouTube 视频字幕提取与分析 | 行业会议、技术分享、案例研究的转录 |
| `web_search` | 网络搜索（内置工具） | 快速查找行业资讯、公司信息、案例 |

### 二、知识管理与体系化沉淀

| 技能 | 用途 | 典型场景 |
|------|------|---------|
| `llm-wiki` | Karpathy 式知识库（三层架构） | 积累行业知识、实体/概念/对比页面、持续更新 |
| `obsidian` | Obsidian 笔记管理 | 可视化浏览知识网络、图谱视图、笔记链接 |
| `notion` | Notion API 集成 | 团队协作、数据库管理、项目看板 |

**关键能力：** 每次摄入新信息时，自动检查现有知识库、创建/更新相关页面、建立交叉引用，形成持续增长的"第二大脑"。

### 三、数据分析与建模

| 技能 | 用途 | 典型场景 |
|------|------|---------|
| `jupyter-live-kernel` | 交互式 Python 数据分析 | 探索行业数据集、快速建模、可视化 |
| `dspy` | 声明式 LM 编程框架 | 构建 AI 评估 pipeline、自动优化提示词 |
| `evaluating-llms-harness` | LLM 基准测试 | 评估不同模型在特定任务上的表现 |
| `weights-and-biases` | 实验追踪 | ML 实验管理、模型性能对比 |

### 四、规划与方案设计

| 技能 | 用途 | 典型场景 |
|------|------|---------|
| `plan` | 规划模式（只设计方案不执行） | 大方向讨论时的方案输出 |
| `writing-plans` | 详细实施方案撰写 | 拆解复杂任务、生成可执行步骤 |
| `subagent-driven-development` | 多 Agent 协作执行 | 并行处理多个独立分析任务 |
| `kanban-orchestrator` | 任务编排与分解 | 大型咨询项目的分阶段管理 |
| `ideation` | 创意生成 | 头脑风暴、方案发散、创新场景探索 |

### 五、沟通与协作

| 技能 | 用途 | 典型场景 |
|------|------|---------|
| `email (himalaya)` | 终端邮件收发 | 客户沟通、项目跟进 |
| `google-workspace` | Google Docs/Sheets/Slides | 协作文档、在线表格、团队共享 |
| `teams-meeting-pipeline` | Teams 会议摘要 pipeline | 自动会议纪要生成 |
| `wechat-messaging` | 微信消息发送 | 快速推送摘要给客户/团队 |

### 六、咨询交付物输出

| 技能 | 用途 | 典型场景 |
|------|------|---------|
| `powerpoint` | PPT 幻灯片创建/编辑 | 方案汇报、客户演示、培训材料 |
| `baoyu-infographic` | 信息图生成（21布局×21风格） | 行业洞察可视化、数据故事、一页纸摘要 |
| `architecture-diagram` | 技术架构图（暗色主题 SVG） | 系统方案图、AI 架构设计、技术路线图 |
| `excalidraw` | 手绘风格图表（JSON 格式） | 流程图、概念图、白板风格演示 |
| `baoyu-article-illustrator` | 文章配图生成 | 白皮书/方案书插图 |
| `baoyu-comic` | 知识漫画 | 培训材料、科普内容 |
| `humanizer` | 文本去 AI 化 | 确保报告/方案读起来像人写的，非 AI 腔 |
| `design-md` | Google 设计令牌规范 | 统一品牌视觉（配色、字体、圆角等） |
| `claude-design` | HTML 原型/落地页 | 快速制作交互原型或演示页面 |
| `nano-pdf` | PDF 文本编辑 | 修改 PDF 中的笔误、标题等 |

### 七、自动化与持续运营

| 技能 | 用途 | 典型场景 |
|------|------|---------|
| `cronjob` | 定时任务调度 | 每周行业简报自动生成、定期数据抓取 |
| `webhook-subscriptions` | Webhook 事件订阅 | 外部事件触发自动分析 |

---

## 典型咨询工作流示例

### 场景 A：行业 AI 应用调研报告

```
1. arxiv + blogwatcher → 收集 AI 领域最新论文和博客
2. web-scraping + web_search → 收集行业案例和公司实践
3. llm-wiki → 体系化沉淀，建立实体/概念知识网络
4. jupyter-live-kernel → 数据分析，量化趋势
5. humanizer → 润色报告文本
6. baoyu-infographic → 生成关键洞察信息图
7. powerpoint → 制作客户汇报 PPT
8. cronjob → 设置月度更新（持续追踪）
```

### 场景 B：AI 战略方案咨询

```
1. web_search + polymarket → 市场趋势和预测数据
2. ideation → 头脑风暴潜在 AI 应用场景
3. plan → 产出方案框架
4. writing-plans → 细化实施方案
5. architecture-diagram → 绘制技术架构图
6. excalidraw → 绘制业务流程图
7. design-md → 统一视觉规范
8. powerpoint → 最终方案演示
9. email → 发送给客户
```

### 场景 C：传统业务诊断与 AI 机会识别

```
1. ocr-and-documents → 提取行业报告、内部文档
2. web-scraping → 收集行业标杆数据
3. jupyter-live-kernel → 差距分析、数据建模
4. dspy → 构建 AI 评估 pipeline
5. baoyu-infographic → 可视化诊断结果
6. powerpoint → 差距分析与建议报告
```

---

## 项目目录结构

```
SSG_AI/
├── README.md           # 本文件 — 项目总览和能力清单
├── research/           # 研究原材料
│   ├── papers/         #   学术论文
│   ├── articles/       #   行业文章
│   ├── reports/        #   行业报告
│   └── transcripts/    #   访谈/会议记录
├── analysis/           # 分析产出
│   ├── benchmarks/     #   对标分析
│   ├── models/         #   分析模型/框架
│   └── insights/       #   洞察总结
├── outputs/            # 最终交付物
│   ├── decks/          #   PPT 文件
│   ├── reports/        #   书面报告
│   ├── infographics/   #   信息图
│   └── diagrams/       #   架构图/流程图
├── notes/              # 工作笔记（可关联 Obsidian/Wiki）
└── references/         # 参考资料和模板
```

---

## 下一步

1. 确定首个咨询课题（如特定行业的 AI 应用调研、某传统业务的 AI 机会评估）
2. 配置知识库（Wiki + Obsidian）作为项目的长期知识沉淀平台
3. 建立信息源（RSS 订阅、关键词监控）实现持续情报输入
4. 产出首个交付物（调研报告 / 信息图 / 方案书）
