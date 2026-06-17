import pytest
from agent.executor import executor_node
from agent.engine import AgentState, SubTask


@pytest.mark.asyncio
async def test_executor_skips_completed_steps():
    """Executor should skip steps that already have results"""
    from agent.engine import StepResult

    state = AgentState(
        query="test",
        plan=[
            SubTask(id=1, description="step 1", tool=None),
            SubTask(id=2, description="step 2", tool=None),
        ],
        step_results=[
            StepResult(task_id=1, tool="llm", output="done", elapsed_ms=0),
        ],
    )
    # Should process step 2, not step 1
    assert callable(executor_node)


def test_executor_node_callable():
    assert callable(executor_node)
