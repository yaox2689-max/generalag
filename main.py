from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from config import settings

app = FastAPI(title="General Agent", version="0.1.0")

FRONTEND_DIST = Path(__file__).parent / "frontend" / "dist"

# Shared memory manager (per-process singleton)
_memory_manager = None


def get_memory():
    global _memory_manager
    if _memory_manager is None:
        from memory.manager import MemoryManager
        _memory_manager = MemoryManager()
    return _memory_manager


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


@app.post("/query/stream")
async def query_stream(req: QueryRequest):
    import json
    from asyncio import Queue

    from agent.engine import AgentEngine
    from tools.registry import ToolRegistry

    ToolRegistry.discover()
    event_queue: Queue = Queue()

    async def on_event(event: dict):
        await event_queue.put(event)

    async def generate():
        engine = AgentEngine(on_event=on_event)

        # Run engine in background
        import asyncio
        run_task = asyncio.create_task(engine.run(req.query))

        # Stream events as they arrive
        while not run_task.done() or not event_queue.empty():
            try:
                event = await asyncio.wait_for(event_queue.get(), timeout=0.1)
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
            except asyncio.TimeoutError:
                continue

        # Get final result
        result = await run_task
        final = {
            "type": "final_answer",
            "answer": result.answer,
            "domain": result.domain,
            "complexity": result.complexity,
            "sources": result.sources,
            "steps": [{"task_id": s.task_id, "tool": s.tool, "output": s.output[:500]} for s in result.steps],
            "elapsed_ms": result.elapsed_ms,
        }
        yield f"data: {json.dumps(final, ensure_ascii=False)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.app_host, port=settings.app_port, reload=True)


# Serve frontend static files (production mode)
if FRONTEND_DIST.exists():
    from fastapi.staticfiles import StaticFiles

    @app.get("/")
    async def serve_frontend():
        return FileResponse(FRONTEND_DIST / "index.html")

    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="static")
