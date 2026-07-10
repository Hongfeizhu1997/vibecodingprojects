# Decisions

> GPS Cost Pricing Workbench 持久化决策记录。只增不改。

---

## 2026-05 — 数据存储：SQLite + CSV 双通道

- **Status**: Active
- **Context**: 需要持久化定价数据，同时保留 CSV 导入/导出兼容性。纯文件方案缺乏审计，纯数据库方案不方便外部工具查看。
- **Decision**: SQLite 作为主存储，CSV 作为导入/导出通道。通过 custom server 实现双向同步（CSV ↔ SQLite）。
- **Consequence**: 
  - 必须使用 `python3 server.py` 启动，不能用标准 http.server
  - CSV 导入自动同步到 SQLite，CSV 导出从 SQLite 生成
  - `pricing_master.db` 不上传 Git

---

## 2026-05 — 字段审计：完整字段追踪

- **Status**: Active
- **Context**: 定价数据变更需要可追溯，以便审计和历史对比。
- **Decision**: 每次数据修改记录完整字段快照（cycle_name, service_pn, country, service_tier 等全部字段），而非仅记录变更字段。
- **Consequence**: 
  - 数据库表包含完整的审计时间戳
  - Dashboard 可以展示定价历史趋势
  - 每行数据包含完整的字段集（共 17 列）

---

## 2026-05 — 前端架构：每 Stage 独立页面 + 共享导航

- **Status**: Active
- **Context**: 6 个 Stage 各有不同的输入/输出/业务逻辑，放在单页会过于复杂。
- **Decision**: 每个 Stage 独立 HTML 页面（stage3~6_browser/），共享顶部导航栏，Launcher 页面作为入口。
- **Consequence**: 
  - 各 Stage 独立开发/测试，互不阻塞
  - 导航栏在所有页面保持一致
  - `shared/` 目录存放跨 Stage 共享逻辑

---

## 2026-05 — 测试策略：YAML Spec 驱动 + 自动化 108 测试

- **Status**: Active
- **Context**: 定价逻辑复杂，手动测试容易遗漏。
- **Decision**: 使用 YAML 定义测试 Spec（tests/specs/stage*.yaml），自动运行并生成 JSON + MD 双格式报告。全部 108 测试通过。
- **Consequence**: 
  - 修改定价逻辑后必须运行全部测试
  - 测试报告自动存档在 tests/reports/
  - 新增 Stage 需同步新增 YAML spec

---

## 2026-06 — UI 设计语言：浅色主题 + Montserrat 字体

- **Status**: Active
- **Context**: Dashboard 和 Stage 页面需要统一的视觉风格，以提升业务用户信任感。
- **Decision**: 采用浅色主题（白底 + 蓝色主色调），Montserrat 字体，卡片式布局。禁止深色主题切换。
- **Consequence**: 
  - 所有新增页面必须沿用此设计语言
  - 字体、配色、按钮样式不得随意更换
  - 与 SSG AI 其他项目（深色 HTML）的设计语言不共享

---

## 2026-06 — 版本管理：fork 后覆盖策略

- **Status**: Active
- **Context**: GPS Workbench v5.0 已成熟，需防止修改破坏已有功能。
- **Decision**: 成熟版本修改前，先 fork 新文件（如 v2/v3），迭代确认无误后再覆盖旧版本。不直接在成熟产出上修改。
- **Consequence**: 
  - 重大修改前先建 fork 版本
  - _archive/ 存放被替代的旧版本
  - 降低了回滚成本
