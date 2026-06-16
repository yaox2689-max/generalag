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


@app.get("/health")
async def health():
    return {"status": "ok", "model": settings.llm_model}


@app.post("/query", response_model=QueryResponse)
async def query_agent(req: QueryRequest):
    from agent.graph import compile_graph
    from tools.registry import ToolRegistry

    ToolRegistry.discover()
    graph = compile_graph()

    initial_state = {
        "query": req.query,
        "domain": "",
        "complexity": "",
        "plan": [],
        "current_step": 0,
        "step_results": [],
        "final_answer": "",
        "sources": [],
        "verification": {"is_sufficient": False, "gaps": [], "score": 0.0},
        "retry_count": 0,
    }

    result = await graph.ainvoke(initial_state)

    return QueryResponse(
        answer=result.get("final_answer", ""),
        domain=result.get("domain", ""),
        complexity=result.get("complexity", ""),
        sources=result.get("sources", []),
        steps=result.get("step_results", []),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.app_host, port=settings.app_port, reload=True)
