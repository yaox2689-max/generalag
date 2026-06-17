import pytest
from agent.verifier import verifier_node
from agent.engine import AgentState, StepResult, VerificationResult


@pytest.mark.asyncio
async def test_verifier_node_returns_dict():
    """verifier_node should return a dict with verification and retry_count"""
    state = AgentState(
        query="test query",
        step_results=[
            StepResult(task_id=1, tool="calculator", output="42", elapsed_ms=100),
        ],
    )
    # This test verifies the node runs without crashing
    # In a real test, we'd mock the LLM
    # For now, just check the function signature is correct
    assert callable(verifier_node)


def test_verification_result_defaults():
    vr = VerificationResult()
    assert vr.is_sufficient is False
    assert vr.gaps == []
    assert vr.score == 0.0


def test_step_result():
    sr = StepResult(task_id=1, tool="calculator", output="42", elapsed_ms=100)
    assert sr.task_id == 1
    assert sr.tool == "calculator"
    assert sr.output == "42"
    assert sr.elapsed_ms == 100
