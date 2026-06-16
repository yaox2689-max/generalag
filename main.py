from fastapi import FastAPI
from pydantic import BaseModel

from config import settings

app = FastAPI(title="General Agent", version="0.1.0")


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str
    domain: str
    complexity: str
    sources: list[str]
    steps: list[dict]
    elapsed_ms: int


@app.get("/health")
async def health():
    return {"status": "ok", "model": settings.llm_model}


@app.post("/query", response_model=QueryResponse)
async def query_agent(req: QueryRequest):
    from agent.engine import AgentEngine
    from tools.registry import ToolRegistry

    ToolRegistry.discover()
    engine = AgentEngine()
    result = await engine.run(req.query)

    return QueryResponse(
        answer=result.answer,
        domain=result.domain,
        complexity=result.complexity,
        sources=result.sources,
        steps=[{"task_id": s.task_id, "tool": s.tool, "output": s.output[:500]} for s in result.steps],
        elapsed_ms=result.elapsed_ms,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.app_host, port=settings.app_port, reload=True)
