# General Agent

可插拔、可扩展的通用智能体框架。采用 Plan-and-Execute 模式，以金融研究助手作为 Demo 场景，框架本身领域无关。

## 架构

```
Router ──→ simple ──→ [single tool] ──→ Writer → END
    └──→ complex ──→ Planner → [Executor → Verifier] × N → Writer → END
```

### 核心模块

| 模块 | 职责 |
|------|------|
| `agent/` | LangGraph 状态机：Router → Planner → Executor → Verifier → Writer |
| `tools/` | 可插拔工具系统，自动发现，继承 BaseTool 即可扩展 |
| `knowledge/` | 文档入库、分块、检索优化 |
| `evaluation/` | Golden Sample 管理 + 多维度自动评分 |
| `memory/` | 三层记忆：Working / Summary / Long-term |
| `api/` | FastAPI 路由 |

### 内置工具

- `calculator` — 数学计算 (sympy)
- `rag_search` — 本地知识库检索 (Milvus)
- `web_search` — 网络搜索
- `text_summarizer` — 文本摘要
- `financial_report` — 财报查询 (AKShare)

## 快速开始

```bash
# 安装依赖
uv sync

# 复制环境变量
cp .env.example .env

# 启动服务 (Milvus + PostgreSQL + Redis)
docker compose up -d

# 启动 API
uv run uvicorn main:app --reload
```

访问 http://localhost:8000/health 验证服务状态。

## 技术栈

Python 3.12 / LangGraph / LangChain / Milvus / FastAPI / Vue3 / PostgreSQL / Docker
