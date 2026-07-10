# GPS Cost Pricing Workbench

> Version 5.0 | Lenovo GPS (Global Product Support) — SSGCDTO Division
> 离线定价工具：6 阶段 Pipeline，SQLite + CSV 双通道，字段级审计

---

## 定位

面向 Lenovo GPS 服务定价团队，提供从原始成本数据到可发布 List Price 的完整定价工作流。

- **业务线**：SSG GPS
- **核心场景**：服务 PN 的 Sales Cost 计算、GVE 校验、List Price 推导、梯度检查
- **技术栈**：Python 3 (http.server) + SQLite + CSV + HTML/JS 前端
- **交付模式**：离线工具（浏览器访问本地服务）

---

## 快速开始

```bash
cd GPS_Cost_Pricing_Workbench
python3 server.py 8080
```

打开浏览器访问 **http://localhost:8080/GPS_Cost_Pricing_Workbench.html**

> ⚠️ 必须使用 `python3 server.py`，不能用 `python3 -m http.server`。自定义 server 处理 SQLite + CSV 数据持久化。

---

## 6 阶段 Pipeline

```
Stage 1          Stage 2          Stage 3         Stage 4         Stage 5          Stage 6
Std Cost ──→ Forward Adj ──→ Sales Cost ──→ GVE Validation ──→ List Price ──→ Gradient Check
 (TBD)          (TBD)            ✅ ACTIVE        ✅ ACTIVE        ✅ ACTIVE         ✅ ACTIVE
```

| Stage | 功能 | 状态 |
|-------|------|:--:|
| 1 | Standard Cost 导入 | TBD |
| 2 | Forward Adjustment（历史涨幅调整） | TBD |
| 3 | Sales Cost 计算（Uplift 规则 + 服务属性） | ✅ |
| 4 | GVE 4 层校验（Gap/Validity/Extreme/Reasonability） | ✅ |
| 5 | List Price 推导（PFV 对标） | ✅ |
| 6 | Gradient Check（价格梯度/异常检测） | ✅ |
| Dashboard | 历史定价数据分析 | ✅ |

---

## 项目结构

```
GPS_Cost_Pricing_Workbench/
├── README.md                  ← 本文件
├── DECISIONS.md               ← 架构/设计决策记录
├── GPS_Pricing_UserManual.md  ← 用户操作手册
├── server.py                  ← 主服务（数据持久化 + API）
├── build_manual.py            ← 用户手册构建脚本
├── test_bridge.html           ← 测试桥接页面
├── pricing_master.db          ← SQLite 主数据库（本地，不上传 Git）
├── dashboard_browser/         ← Dashboard 前端
├── stage3_browser/            ← Stage 3 前端
├── stage4_browser/            ← Stage 4 前端
├── stage5_browser/            ← Stage 5 前端
├── stage6_browser/            ← Stage 6 前端
├── shared/                    ← 前后端共享逻辑
├── sample_data/               ← 各阶段样例数据
├── references/                ← 参考资料（不上传 Git）
├── tests/                     ← 测试套件（108/108）
├── docs/                      ← Dashboard 截图/分析报告
├── analysis/                  ← 数据分析产出
└── _archive/                  ← 历史版本归档
```

---

## 日常命令

| 命令 | 用途 |
|------|------|
| `python3 server.py 8080` | 启动服务 |
| `python3 tests/run_tests.py` | 运行全部 108 测试 |

---

## 已知约束

- 仅本地使用，不部署到服务器
- SQLite 数据库不上传 Git（`.gitignore` 已排除）
- CSV 通过 server 双向同步到 SQLite（非手动编辑）
- `_archive/` 中为历史版本，不被构建引用
