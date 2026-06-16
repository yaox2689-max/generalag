import sympy

from tools.base import BaseTool, ToolResult


class CalcTool(BaseTool):
    name = "calculator"
    description = "Evaluate mathematical expressions. Supports algebra, calculus, and symbolic math."
    parameters = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Mathematical expression to evaluate, e.g. '2**10', 'solve(x**2 - 4, x)'",
            }
        },
        "required": ["expression"],
    }

    async def execute(self, expression: str, **kwargs) -> ToolResult:
        try:
            result = sympy.sympify(expression)
            return ToolResult(success=True, output=str(result))
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))
