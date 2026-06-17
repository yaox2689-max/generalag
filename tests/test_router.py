import pytest
from agent.router import rule_based_route, router_node
from agent.engine import AgentState


class TestRuleBasedRoute:
    def test_finance_simple_short(self):
        """Short finance query → simple"""
        result = rule_based_route("茅台利润多少")
        assert result is not None
        domain, complexity = result
        assert domain == "finance"
        assert complexity == "simple"

    def test_finance_simple_keyword(self):
        """Finance + simple keyword → simple"""
        result = rule_based_route("茅台今天股价是多少")
        assert result is not None
        domain, complexity = result
        assert domain == "finance"
        assert complexity == "simple"

    def test_qa_simple_short(self):
        """Short QA query → simple"""
        result = rule_based_route("什么是RAG")
        assert result is not None
        domain, complexity = result
        assert domain == "qa"
        assert complexity == "simple"

    def test_ambiguous_returns_none(self):
        """Ambiguous query → None (falls through to LLM)"""
        result = rule_based_route("请帮我分析一下人工智能的未来发展趋势和对就业市场的影响")
        assert result is None

    def test_non_finance_non_qa_returns_none(self):
        """Non-finance, non-QA → None"""
        result = rule_based_route("写一首关于月亮的诗")
        assert result is None

    def test_finance_long_returns_none(self):
        """Long finance query → None (complex, needs LLM)"""
        result = rule_based_route("请帮我详细分析贵州茅台2024年第三季度的财务报表，包括营收、净利润、毛利率等关键指标，并与去年同期对比")
        assert result is None


@pytest.mark.asyncio
async def test_router_node_rule_based():
    """Router should use rules for clear-cut cases"""
    state = AgentState(query="茅台利润多少")
    result = await router_node(state)
    assert result["domain"] == "finance"
    assert result["complexity"] == "simple"
