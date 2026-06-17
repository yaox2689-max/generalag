import pytest
from agent.engine import AgentEngine, AgentState, SubTask


class TestAgentEngine:
    @pytest.mark.asyncio
    async def test_merge_updates_state(self):
        state = AgentState(query="test")
        updates = {"domain": "finance", "complexity": "simple"}
        result = AgentEngine._merge(state, updates)
        assert result.domain == "finance"
        assert result.complexity == "simple"

    @pytest.mark.asyncio
    async def test_merge_ignores_unknown_keys(self):
        state = AgentState(query="test")
        updates = {"domain": "finance", "unknown_field": "value"}
        result = AgentEngine._merge(state, updates)
        assert result.domain == "finance"
        assert not hasattr(result, "unknown_field") or result.__dict__.get("unknown_field") is None

    @pytest.mark.asyncio
    async def test_engine_init(self):
        engine = AgentEngine()
        assert engine._router is not None
        assert engine._planner is not None
        assert engine._executor is not None
        assert engine._verifier is not None
        assert engine._writer is not None
        assert engine._on_event is None

    @pytest.mark.asyncio
    async def test_engine_with_on_event(self):
        events = []

        async def collector(event):
            events.append(event)

        engine = AgentEngine(on_event=collector)
        assert engine._on_event is not None

    @pytest.mark.asyncio
    async def test_emit_calls_callback(self):
        events = []

        async def collector(event):
            events.append(event)

        engine = AgentEngine(on_event=collector)
        await engine._emit("step_start", "Router", "test detail")
        assert len(events) == 1
        assert events[0]["type"] == "step_start"
        assert events[0]["step"] == "Router"
        assert events[0]["detail"] == "test detail"

    @pytest.mark.asyncio
    async def test_emit_noop_without_callback(self):
        engine = AgentEngine()
        # Should not raise
        await engine._emit("step_start", "Router")


class TestAgentState:
    def test_default_state(self):
        state = AgentState(query="hello")
        assert state.query == "hello"
        assert state.domain == ""
        assert state.complexity == ""
        assert state.plan == []
        assert state.step_results == []
        assert state.retry_count == 0

    def test_subtask_defaults(self):
        task = SubTask(id=1, description="test")
        assert task.tool is None
        assert task.depends_on == []
