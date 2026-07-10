# 项目名称

> 一句话描述项目定位和核心价值

---

## 定位

- **业务线**：
- **核心场景**：
- **技术栈**：
- **交付模式**：离线工具 / Web 应用 / 混合 / 自动化

---

## 快速开始

```bash
# 启动
cd project-name
python3 server.py 8080

# 测试
python3 -m pytest tests/ -v

# 构建（如有）
bash scripts/build.sh
```

---

## 项目结构

```
project-name/
├── README.md                  ← 本文件
├── PRODUCT_REQUIREMENTS.md    ← 目标、用户、功能需求
├── DECISIONS.md               ← 持久化架构/技术决策（只增不改）
├── SESSION_HANDOFF.md         ← 跨会话交接（当前状态+下一步）
├── src/                       ← 源代码
│   ├── core/                  ←   共享业务逻辑
│   ├── ui/                    ←   渲染/交互
│   └── parsers/               ←   解析器（按需）
├── scripts/                   ← 构建/检查/发版脚本
├── tests/                     ← 测试 + tests/README.md
├── docs/                      ← 用户手册、QA 计划、上线方案
├── outputs/                   ← 最终交付物
├── references/                ← 参考资料（不上传 Git）
└── archive/                   ← 历史工具/废弃实验
```

---

## 日常命令

| 命令 | 用途 |
|------|------|
| `python3 server.py` | 启动服务 |
| `python3 -m pytest tests/` | 运行全部测试 |
| `python3 -m pytest tests/ -k "stage3"` | 按模块筛选 |

---

## 版本管理

- Git 管理，`release/` 为构建产物不手改
- 发版前：全部测试通过 + 工作树干净
- `.gitignore` 排除 secret、cache、build 产物

---

## 运行约束

- 离线优先 / 需要网络 / 需要数据库
- 依赖项见 `requirements.txt`（如有）
