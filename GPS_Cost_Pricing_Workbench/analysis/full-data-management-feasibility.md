# GPS Cost Pricing Workbench — 全量数据管理方案可行性评估

> 评估日期：2026-06-25 | 版本：v1.0
> 背景：Wave 3a Vladimir 反馈 Domain E — 工具能否从「个人计算器」升级为「GPS 团队全量定价数据管理平台」

---

## 一、需求定义：「全量数据管理」是什么

从 Vladimir 反馈和当前工具定位推导，全量数据管理应覆盖：

| 能力 | 当前状态 | 全量目标 |
|------|:---:|------|
| PN 覆盖 | 单次导入，手动管 | 全部 2,014 活跃 PN 持续追踪 |
| 周期管理 | 单 Cycle 手动命名 | 多 Cycle 自动归档、跨期对比 |
| 历史回溯 | CSV 文件 + Dashboard 简单查询 | 任意 PN 任意时间点定价快照 |
| 数据进出 | CSV 导入/导出 | 对接上游系统（Wukong/SPEP）+ Excel 双向 |
| 团队使用 | 单人 | 2-5 人 GPS 定价团队 |
| 审计追溯 | 基础操作日志 | 谁在何时改了什么、为什么 |

### 数据量估算

```
2,014 PNs × 5 GEOs × 4 Cycles/年 × 3 年 ≈ 120,840 条记录
每条 ~15 字段 ≈ 200 bytes → 总计 ~24 MB（CSV 格式）
```

**结论：数据量极小，不存在规模瓶颈。瓶颈不在量，在架构形态。**

---

## 二、六维度可行性评估

### 2.1 性能

| 评估项 | 结论 |
|--------|------|
| 单次导入 | 2,014 条 × 流式导入（已实现）→ < 3 秒 ✅ |
| 查询/筛选 | IndexedDB 索引扫描 120K 条 → < 100ms ✅ |
| Dashboard 加载 | `/api/load-master` 120K 行 JSON → ~6MB 传输，首屏 ~2 秒 ⚠️ |
| 跨期对比计算 | 前端 JS 内存聚合，120K 条 → < 500ms ✅ |

**判定：✅ 可行。当前架构（流式导入 + IndexedDB + CSV）对 120K 条完全够用。唯一关注点是 Dashboard 首次加载大数据集时的传输时间，可通过分页 API 解决。**

---

### 2.2 存储

| 方案 | 优点 | 缺点 | 判定 |
|------|------|------|:---:|
| **CSV（当前）** | 人类可读、Excel 直接打开、零依赖 | 无索引、并发写不安全、无类型约束 | 够用但不理想 |
| **SQLite** | 索引查询、事务安全、单文件、Python 标准库 | 需改 server.py、前端无法直读（需 API） | 推荐 |
| **Supabase/云 DB** | 多人协作天然支持 | 需网络、需付费、过度设计 | 不需要 |

**判定：⚠️ CSV 可继续用但不建议长期。推荐升级到 SQLite**——单文件零部署、server.py 原生支持（`import sqlite3`）、保留「Excel 可打开」优势（SQLite 可导出 CSV）。

**对比**：

```
CSV 模式（当前）：        SQLite 模式（推荐）：
Stage 3 → CSV upsert      Stage 3 → POST /api/save → SQLite UPSERT
Dashboard ← CSV parse     Dashboard ← GET /api/query?pn=xxx → JSON
备份 = cp pricing.csv     备份 = sqlite3 .dump 或导出 CSV
```

---

### 2.3 集成

| 集成点 | 当前能力 | 需要什么 | 判定 |
|--------|---------|---------|:---:|
| **上游：Wukong PSC 导入** | CSV 手动导入 ✅ | 已有，不需要改 | ✅ |
| **上游：SPEP/SCFE 拉取** | 无 | 需要 API 对接或定期 CSV 导出 | 🔶 |
| **下游：Excel 消费** | CSV 导出 ✅ | 已有 | ✅ |
| **下游：DeerFlow/Vetraflow** | 无 | 如果是未来目标，需 REST API | 🔶 |
| **Excel 双向同步** | 单向（导入/导出独立） | 需要「从 Excel 更新已有记录」能力 | 🔶 |

**判定：⚠️ 核心导入导出已通。上下游系统对接是外部依赖问题（需要对方提供接口或 CSV），不是工具架构问题。当前最务实的路径：保持 CSV 作为通用交换格式，不强行做实时 API 集成。**

---

### 2.4 权限

| 场景 | 当前能力 | 差距 |
|------|---------|------|
| 单人使用 | ✅ 完整支持 | — |
| 2-3 人共享一台机器 | ❌ 不支持 | 浏览器 localStorage + CSV 文件，无用户隔离 |
| 团队各自独立定价 | ❌ 不支持 | 需要账号体系 + 数据隔离 |
| 审批流（定价→审核→发布） | ❌ 不支持 | 需要状态机 + 角色权限 |

**判定：❌ 当前架构不支持多人。但——GPS 定价团队规模（2-5 人）决定不需要 RBAC 系统。**

**务实方案**：不建账号体系，用「工作副本」模式——每人一个 CSV 文件（`pricing_张三.csv`），server.py 启动时指定 `--user 张三`。多人在不同时间定价，手动合并。适合 2-5 人团队。

---

### 2.5 协作

| 场景 | 方案 |
|------|------|
| 同一个人跨机器使用 | `git pull/push pricing_master.csv` ✅ |
| 多人同时定价（冲突） | 当前 CSV 没有行级锁 → 后写覆盖先写 ❌ |
| 多人先后定价（无冲突） | 各自工作副本 → 定期合并 → 可行 |

**判定：⚠️ 不支持实时协作。对于 2-5 人团队，用 Git 管理 CSV 版本是最务实的方案——改动可见、可回滚、无额外依赖。只有需要「两人同时定价同一个 PN」时才需要升级到 SQLite + WAL 模式。**

---

### 2.6 审计

| 需求 | 当前能力 | 差距 |
|------|---------|------|
| 记录谁改了什么 | ✅ audit-log.js（操作级） | 仅前端日志，浏览器清缓存即丢失 |
| 回溯 PN 定价变化 | ⚠️ pricing_master.csv 每次 upsert | 只保留最新值，无历史版本 |
| 对比「上次定价 vs 本次」 | ❌ | 需要版本化存储 |
| 审计报告导出 | ❌ | 需要服务端持久化日志 |

**判定：⚠️ 基础审计有但不持久。关键缺口是「PN 定价版本历史」——当前 upsert 覆盖旧值，无法回答「上次 list_price 是多少、谁改的」。**

---

## 三、总体可行性结论

| 维度 | 判定 | 说明 |
|------|:---:|------|
| 性能 | ✅ | 120K 条完全无压力 |
| 存储 | ⚠️ | CSV 可用但不理想，建议 SQLite |
| 集成 | ⚠️ | 核心流程通，上下游依赖外部 |
| 权限 | ❌ | 单用户架构，需改造支持多人 |
| 协作 | ⚠️ | 不支持实时，Git+CSV 可应对 |
| 审计 | ⚠️ | 缺版本历史和持久化 |

### 一句话结论

**可以做。数据量不是瓶颈，瓶颈在单用户架构和 CSV 无法保留历史版本。核心改造不超过 3 个文件、约 500 行代码。不需要上云、不需要数据库服务器、不需要账号系统。**

---

## 四、分阶段实施方案

### Phase 4a：数据层升级（2-3 天）🔴 核心

**目标**：CSV → SQLite + 版本化存储

**改动**：
```
server.py           → sqlite3 替代 CSV（～80 行改动）
pricing_master.db   → 新建，替代 pricing_master.csv
pricing-db.js       → 无改动（前端仍通过 POST/GET API 交互）
```

**SQLite Schema**：
```sql
CREATE TABLE pricing_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cycle_name TEXT NOT NULL,
    service_pn TEXT NOT NULL,
    country TEXT,
    service_tier TEXT,
    upgrade_years TEXT,
    delivery_type TEXT,
    aipc TEXT,
    psc_value REAL,
    sales_cost REAL,
    gve_status TEXT,
    list_price REAL,
    channel_price REAL,
    gp_percent REAL,
    gradient_status TEXT,
    updated_by TEXT DEFAULT 'system',
    updated_at TEXT DEFAULT (datetime('now')),
    UNIQUE(cycle_name, service_pn)
);

CREATE TABLE pricing_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cycle_name TEXT,
    service_pn TEXT,
    field_name TEXT,
    old_value TEXT,
    new_value TEXT,
    changed_by TEXT,
    changed_at TEXT DEFAULT (datetime('now'))
);
```

**新增 API**：
```
GET  /api/load-master        → 同现在，从 SQLite 读取
POST /api/save-master        → 同现在，先记 history 再 upsert
GET  /api/pn-history?pn=xxx  → 返回某 PN 全部历史版本 ← 新
GET  /api/audit-log?pn=xxx   → 返回某 PN 变更记录 ← 新
GET  /api/export-csv         → 导出完整 CSV（保留 Excel 兼容）
```

**交付物**：
- `server.py` 升级为 SQLite 版本
- `pricing_master.db` 替代 `pricing_master.csv`
- Dashboard 增加 PN 历史趋势图（已有框架，扩展即可）
- `pricing_master.csv` 降级为导出格式（按需生成）

---

### Phase 4b：多人使用支持（1-2 天）🟡 条件触发

**触发条件**：当团队实际需要 2+ 人使用时启动。

**方案**：工作副本模式（不建账号体系）

```bash
# 启动时指定用户
python3 server.py 8080 --user zhangsan
# → 使用 pricing_zhangsan.db

python3 server.py 8081 --user lisi
# → 使用 pricing_lisi.db
```

**不需要**：登录页、RBAC、OAuth、Session 管理。

**合并策略**：定期导出各自 CSV → 人工 review → 合并到主库（低频操作，2-5 人团队完全可行）。

---

### Phase 4c：审计 + 审批（1-2 天）🟡 可选

**触发条件**：当需要「谁改了什么、为什么」的正式审计时启动。

**内容**：
- `pricing_history` 表已记录所有变更（Phase 4a 自带）
- 新增「定价状态」字段：`draft → submitted → approved → released`
- Dashboard 增加「待审批」视图（按状态筛选）
- 审批操作：点击「Approve」→ 写 history 记录

**不需要**：工作流引擎、邮件通知、SLA 追踪。

---

### 路线图总览

```
现在 (v4.0)          Phase 4a          Phase 4b         Phase 4c
CSV + http.server → SQLite + history → 多用户副本  → 审批流 + 审计报告
单个用户             3 个文件改动        启动参数        Dashboard 筛选视图
                     核心改造            条件触发        可选
```

**推荐立即推进 Phase 4a**——改动量小、风险低、为后续所有能力打地基。
