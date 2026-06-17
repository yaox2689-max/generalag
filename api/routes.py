import json
import asyncio
from asyncio import Queue

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from config import settings

router = APIRouter()


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str
    domain: str
    complexity: str
    sources: list[str]
    steps: list[dict]
    elapsed_ms: int


@router.get("/health")
async def health():
    return {"status": "ok", "model": settings.llm_model}


@router.post("/query", response_model=QueryResponse)
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


@router.post("/query/stream")
async def query_stream(req: QueryRequest):
    from agent.engine import AgentEngine
    from tools.registry import ToolRegistry

    ToolRegistry.discover()
    event_queue: Queue = Queue()

    async def on_event(event: dict):
        await event_queue.put(event)

    async def generate():
        engine = AgentEngine(on_event=on_event)
        run_task = asyncio.create_task(engine.run(req.query))

        while not run_task.done() or not event_queue.empty():
            try:
                event = await asyncio.wait_for(event_queue.get(), timeout=0.1)
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
            except asyncio.TimeoutError:
                continue

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
