from duckduckgo_search import DDGS

from tools.base import BaseTool, ToolResult


class SearchTool(BaseTool):
    name = "web_search"
    description = "Search the web for up-to-date information using DuckDuckGo."
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query string",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return (default 5)",
                "default": 5,
            },
        },
        "required": ["query"],
    }

    async def execute(self, query: str, max_results: int = 5, **kwargs) -> ToolResult:
        try:
            results = DDGS().text(query, max_results=max_results)
            formatted = []
            for i, r in enumerate(results, 1):
                formatted.append(f"[{i}] {r['title']}\n    {r['href']}\n    {r['body']}")
            output = "\n\n".join(formatted)
            return ToolResult(
                success=True,
                output=output,
                metadata={"num_results": len(results)},
            )
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))
