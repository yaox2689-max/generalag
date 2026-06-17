import logging
import time
from dataclasses import dataclass, field
from typing import Callable, Awaitable

logger = logging.getLogger(__name__)

MAX_RETRIES = 3

EventCallback = Callable[[dict], Awaitable[None]] | None


@dataclass
class StepResult:
    task_id: int
    tool: str
    output: str
    elapsed_ms: int = 0


@dataclass
class VerificationResult:
    is_sufficient: bool = False
    gaps: list[str] = field(default_factory=list)
    score: float = 0.0


@dataclass
class SubTask:
    id: int
    description: str
    tool: str | None = None
    depends_on: list[int] = field(default_factory=list)


@dataclass
class AgentState:
    query: str
    domain: str = ""
    complexity: str = ""  # "simple" / "complex"
    plan: list[SubTask] = field(default_factory=list)
    current_step: int = 0
    step_results: list[StepResult] = field(default_factory=list)
    final_answer: str = ""
    sources: list[str] = field(default_factory=list)
    verification: VerificationResult = field(default_factory=VerificationResult)
    retry_count: int = 0


@dataclass
class AgentResult:
    answer: str
    domain: str
    complexity: str
    sources: list[str]
    steps: list[StepResult]
    verification: VerificationResult
    elapsed_ms: int


class AgentEngine:
    """
    Self-built agent orchestration engine.
    Implements Plan-and-Execute with fast path, no LangGraph dependency.
    """

    def __init__(self, memory: "MemoryManager | None" = None, on_event: EventCallback = None):
        from agent.router import router_node
        from agent.planner import planner_node
        from agent.executor import executor_node
        from agent.verifier import verifier_node
        from agent.writer import writer_node

        self._router = router_node
        self._planner = planner_node
        self._executor = executor_node
        self._verifier = verifier_node
        self._writer = writer_node
        self._memory = memory
        self._on_event = on_event

    async def run(self, query: str) -> AgentResult:
        start = time.monotonic()

        # Memory: record user message and recall relevant context
        if self._memory:
            await self._memory.on_user_message(query)

        state = AgentState(query=query)

        # Phase 1: Route
        await self._emit("step_start", "Router")
        state = await self._route(state)
        await self._emit("step_done", "Router", f"Domain: {state.domain} | {state.complexity}")
        logger.info("Routed: domain=%s complexity=%s", state.domain, state.complexity)

        # Phase 2: Execute (with or without planning)
        if state.complexity == "simple":
            state = await self._execute_simple(state)
        else:
            state = await self._execute_complex(state)

        # Phase 3: Write final answer
        await self._emit("step_start", "Writer")
        state = await self._writer(state)
        await self._emit("step_done", "Writer", "Answer generated")

        # Memory: record agent response
        if self._memory:
            await self._memory.on_agent_response(state.final_answer)

        elapsed_ms = int((time.monotonic() - start) * 1000)
        return AgentResult(
            answer=state.final_answer,
            domain=state.domain,
            complexity=state.complexity,
            sources=state.sources,
            steps=state.step_results,
            verification=state.verification,
            elapsed_ms=elapsed_ms,
        )

    async def _route(self, state: AgentState) -> AgentState:
        updates = await self._router(state)
        return self._merge(state, updates)

    async def _execute_simple(self, state: AgentState) -> AgentState:
        """Fast path: single tool call, skip planning and verification."""
        state.plan = [SubTask(id=1, description=state.query, tool=None)]
        await self._emit("step_start", "Executor")
        updates = await self._executor(state)
        state = self._merge(state, updates)
        tool_names = ", ".join(set(s.tool for s in state.step_results)) or "llm"
        await self._emit("step_done", "Executor", f"Tools: {tool_names}")
        return state

    async def _execute_complex(self, state: AgentState) -> AgentState:
        """Full path: plan → execute → verify loop."""
        # Plan
        await self._emit("step_start", "Planner")
        updates = await self._planner(state)
        state = self._merge(state, updates)
        await self._emit("step_done", "Planner", f"{len(state.plan)} subtask(s)")

        # Execute-verify loop
        for attempt in range(MAX_RETRIES):
            # Execute all steps
            await self._emit("step_start", "Executor")
            while True:
                executed_before = len(state.step_results)
                updates = await self._executor(state)
                state = self._merge(state, updates)
                if len(state.step_results) == executed_before:
                    break
            tool_names = ", ".join(set(s.tool for s in state.step_results)) or "llm"
            await self._emit("step_done", "Executor", f"Tools: {tool_names}")

            # Verify
            await self._emit("step_start", "Verifier")
            updates = await self._verifier(state)
            state = self._merge(state, updates)
            await self._emit("step_done", "Verifier", f"Score: {state.verification.score:.1f}")

            if state.verification.is_sufficient:
                logger.info("Verification passed on attempt %d", attempt + 1)
                break
            logger.info(
                "Verification failed (attempt %d/%d), gaps: %s",
                attempt + 1, MAX_RETRIES, state.verification.gaps,
            )

        return state

    @staticmethod
    def _merge(state: AgentState, updates: dict) -> AgentState:
        for key, value in updates.items():
            if hasattr(state, key):
                setattr(state, key, value)
        return state

    async def _emit(self, event_type: str, step: str, detail: str = "") -> None:
        if self._on_event:
            await self._on_event({"type": event_type, "step": step, "detail": detail})
