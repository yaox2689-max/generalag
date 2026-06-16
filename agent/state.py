from typing import TypedDict


class SubTask(TypedDict):
    id: int
    description: str
    tool: str | None
    depends_on: list[int]


class StepResult(TypedDict):
    task_id: int
    tool: str
    output: str
    elapsed_ms: int


class VerificationResult(TypedDict):
    is_sufficient: bool
    gaps: list[str]
    score: float


class AgentState(TypedDict):
    query: str
    domain: str
    complexity: str  # "simple" / "complex"
    plan: list[SubTask]
    current_step: int
    step_results: list[StepResult]
    final_answer: str
    sources: list[str]
    verification: VerificationResult
    retry_count: int
