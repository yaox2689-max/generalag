# General Agent — Demo

## Quick Start

```bash
# 1. Install dependencies
uv sync

# 2. Set up API key (for full agent flow)
cp .env.example .env
# Edit .env and set OPENAI_API_KEY

# 3. Run demo
uv run python demo/financial_demo.py
```

## What the Demo Does

**Demo 1 (no API key needed):**
- Calls `calculator` tool directly: `2^50`
- Calls `financial_report` tool directly: Moutai (600519) income statement
- Shows that tools work independently without LLM

**Demo 2 (needs API key):**
- Runs the full AgentEngine pipeline
- Shows Router → Planner → Executor → Verifier → Writer flow
- Real-time step events via `on_event` callback
- Financial analysis with AKShare data

## Architecture

```
Router ──→ simple ──→ [Executor] ──→ Writer → END
    └──→ complex ──→ Planner → Executor → Verifier
                          ↑           │
                          └── gaps ←──┘
```
