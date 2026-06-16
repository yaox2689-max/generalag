import json

from langchain_core.messages import HumanMessage, SystemMessage

from agent.llm import get_llm
from agent.engine import AgentState
from tools.registry import ToolRegistry

PLANNER_PROMPT = """You are a task planner. Given a user query and available tools, decompose the query into a sequence of subtasks.

Available tools:
{tool_descriptions}

Output a JSON object with exactly this structure:
{{
  "goal": "one-line summary of the overall goal",
  "subtasks": [
    {{
      "id": 1,
      "description": "what this step does",
      "tool": "tool_name or null if no tool needed",
      "depends_on": []
    }}
  ]
}}

Rules:
- Each subtask should be actionable and specific
- Use the EXACT tool names from the list above
- Set tool to null for synthesis/analysis steps that don't need a tool
- Use depends_on to express ordering constraints
- Keep it concise: 2-5 subtasks is usually enough
- Output ONLY the JSON, no other text."""


def _format_tool_descriptions() -> str:
    lines = []
    for name, tool in ToolRegistry.get_all().items():
        lines.append(f"- {name}: {tool.description}")
    return "\n".join(lines)


async def planner_node(state: AgentState) -> dict:
    llm = get_llm()
    query = state.query
    domain = state.domain or "general"

    prompt = PLANNER_PROMPT.format(tool_descriptions=_format_tool_descriptions())

    resp = await llm.ainvoke([
        SystemMessage(content=prompt),
        HumanMessage(content=f"Domain: {domain}\nQuery: {query}"),
    ])

    try:
        raw = resp.content.strip().removeprefix("```json").removesuffix("```").strip()
        plan = json.loads(raw)
        subtasks = plan.get("subtasks", [])
    except (json.JSONDecodeError, AttributeError):
        # Fallback: single-step plan
        subtasks = [{"id": 1, "description": query, "tool": None, "depends_on": []}]

    return {"plan": subtasks, "current_step": 0, "step_results": []}
