import pytest
from tools.base import BaseTool, ToolResult
from tools.calc_tool import CalcTool
from tools.registry import ToolRegistry


class TestCalcTool:
    @pytest.fixture
    def tool(self):
        return CalcTool()

    @pytest.mark.asyncio
    async def test_basic_arithmetic(self, tool):
        result = await tool(expression="2+3")
        assert result.success is True
        assert result.output == "5"

    @pytest.mark.asyncio
    async def test_exponentiation(self, tool):
        result = await tool(expression="2**10")
        assert result.success is True
        assert result.output == "1024"

    @pytest.mark.asyncio
    async def test_algebra(self, tool):
        result = await tool(expression="x**2 + 2*x + 1")
        assert result.success is True
        assert "x" in result.output

    @pytest.mark.asyncio
    async def test_invalid_expression(self, tool):
        result = await tool(expression="not_a_valid_expr +++")
        assert result.success is False
        assert result.error is not None

    def test_metadata(self, tool):
        assert tool.name == "calculator"
        assert "expression" in tool.parameters["properties"]


class TestToolRegistry:
    def test_discover_finds_tools(self):
        ToolRegistry._tools = {}  # reset
        ToolRegistry.discover()
        tools = ToolRegistry.list_tools()
        assert "calculator" in tools

    def test_get_existing_tool(self):
        tool = ToolRegistry.get("calculator")
        assert tool is not None
        assert tool.name == "calculator"

    def test_get_nonexistent_tool(self):
        tool = ToolRegistry.get("nonexistent_tool")
        assert tool is None


class TestBaseToolRetry:
    @pytest.mark.asyncio
    async def test_retry_on_failure(self):
        call_count = 0

        class FlakyTool(BaseTool):
            name = "flaky"
            description = "fails first 2 times"
            parameters = {"type": "object", "properties": {}}

            async def execute(self, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count < 3:
                    raise RuntimeError("temporary failure")
                return ToolResult(success=True, output="ok")

        tool = FlakyTool()
        result = await tool()
        assert result.success is True
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_returns_error_after_max_retries(self):
        class AlwaysFailTool(BaseTool):
            name = "fail"
            description = "always fails"
            parameters = {"type": "object", "properties": {}}

            async def execute(self, **kwargs):
                raise RuntimeError("permanent failure")

        tool = AlwaysFailTool()
        result = await tool()
        assert result.success is False
        assert "3 retries" in result.error
