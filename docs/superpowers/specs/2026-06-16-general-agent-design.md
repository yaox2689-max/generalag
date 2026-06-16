# General Agent Framework - Design Spec

## Overview

A domain-agnostic Agent framework with pluggable tools, using **金融研究助手** as the primary demo scenario.

## Architecture: Plan-and-Execute with Fast Path

```
Router ──→ simple ──→ [single tool] ──→ Writer → END
    └──→ complex ──→ Planner → [Executor → Verifier] × N → Writer → END
```

### Router (Rules + LLM two-level)
1. Rule layer: keyword matching for clear-cut cases
2. LLM layer: structured output `{domain, complexity, confidence}` for ambiguous cases

### State (LangGraph TypedDict)
```python
class AgentState(TypedDict):
    query: str
    domain: str
    complexity: str                    # "simple" / "complex"
    plan: list[SubTask]
    current_step: int
    step_results: list[StepResult]
    final_answer: str
    sources: list[str]
    verification: VerificationResult
    retry_count: int                   # max 3
```

## Pluggable Tool System

- `BaseTool` (ABC): `name`, `description`, `parameters` (JSON Schema), `execute(**kwargs) -> ToolResult`
- Auto-discovery: scan `tools/*_tool.py` on startup, register subclasses
- Built-in: `rag_tool`, `search_tool`, `calc_tool`, `summary_tool`, `financial_tool` (AKShare)

## Step 1 Scope (Project Skeleton)

- `pyproject.toml` (uv, deps)
- `.env.example`
- `config.py` (pydantic-settings)
- `main.py` (FastAPI + health check)
- `agent/state.py` (TypedDict)
- `agent/graph.py` (LangGraph skeleton with placeholder nodes)
- `tools/base.py` (BaseTool + retry/timeout/logging)
- `tools/registry.py` (auto-discovery)
- `tools/calc_tool.py` (first runnable tool)
- `docker-compose.yml` (Milvus + PostgreSQL + Redis)

## Tech Stack

- Python 3.12, uv
- LangGraph + LangChain Core + LangChain OpenAI (multi-model via OpenAI-compatible API)
- FastAPI + Uvicorn
- Milvus (milvus-lite for dev)
- PostgreSQL, Redis
- pydantic-settings
- httpx, sympy

## Verification (Step 1)

1. `uv run python -c "from tools.registry import ToolRegistry; print(ToolRegistry.list_tools())"` → shows calc_tool
2. `uv run uvicorn main:app` → `/health` returns 200
3. `calc_tool.execute(expression="1+1")` → returns 2
