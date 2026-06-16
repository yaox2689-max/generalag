import json
import logging

from langchain_core.messages import HumanMessage, SystemMessage

from agent.llm import get_llm
from agent.state import AgentState
from tools.registry import ToolRegistry

logger = logging.getLogger(__name__)

EXECUTOR_PROMPT = """You are a tool executor. Given a subtask description and a tool, determine the correct arguments to call the tool.

Tool: {tool_name}
Tool description: {tool_description}
Tool parameters schema: {parameters_schema}
Subtask: {subtask_description}

Previous step results (for context):
{previous_results}

Output a JSON object with the tool arguments. Output ONLY the JSON, no other text."""


def _format_previous_results(step_results: list) -> str:
    if not step_results:
        return "None (first step)"
    lines = []
    for r in step_results:
        lines.append(f"Step {r['task_id']} ({r['tool']}): {r['output'][:300]}")
    return "\n".join(lines)


async def executor_node(state: AgentState) -> dict:
    llm = get_llm()
    plan = state.get("plan", [])
    current_step = state.get("current_step", 0)
    step_results = list(state.get("step_results", []))

    # Find next unexecuted step whose dependencies are met
    executed_ids = {r["task_id"] for r in step_results}

    for task in plan:
        task_id = task["id"]
        if task_id in executed_ids:
            continue
        deps = task.get("depends_on", [])
        if not all(d in executed_ids for d in deps):
            continue

        # This is the next step to execute
        tool_name = task.get("tool")
        if not tool_name:
            # No tool needed — use LLM to synthesize
            synthesis = await llm.ainvoke([
                SystemMessage(content="You are an analyst. Synthesize the following results into a brief conclusion."),
                HumanMessage(content=_format_previous_results(step_results) + f"\n\nTask: {task['description']}"),
            ])
            step_results.append({
                "task_id": task_id,
                "tool": "llm_synthesis",
                "output": synthesis.content[:2000],
                "elapsed_ms": 0,
            })
        else:
            tool = ToolRegistry.get(tool_name)
            if tool is None:
                step_results.append({
                    "task_id": task_id,
                    "tool": tool_name,
                    "output": "",
                    "elapsed_ms": 0,
                })
            else:
                # Ask LLM to generate tool arguments
                prompt = EXECUTOR_PROMPT.format(
                    tool_name=tool.name,
                    tool_description=tool.description,
                    parameters_schema=json.dumps(tool.parameters, ensure_ascii=False),
                    subtask_description=task["description"],
                    previous_results=_format_previous_results(step_results),
                )
                resp = await llm.ainvoke([
                    SystemMessage(content=prompt),
                    HumanMessage(content=f"Generate arguments for tool '{tool_name}' to accomplish: {task['description']}"),
                ])

                try:
                    raw = resp.content.strip().removeprefix("```json").removesuffix("```").strip()
                    args = json.loads(raw)
                except (json.JSONDecodeError, AttributeError):
                    args = {}

                # Execute the tool
                result = await tool(**args)
                step_results.append({
                    "task_id": task_id,
                    "tool": tool_name,
                    "output": result.output[:2000],
                    "elapsed_ms": result.elapsed_ms,
                })
                logger.info("Executed step %d with tool %s: success=%s", task_id, tool_name, result.success)

        # Only execute one step per node call (LangGraph will re-invoke)
        break

    return {"step_results": step_results, "current_step": current_step + 1}
