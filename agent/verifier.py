import json

from langchain_core.messages import HumanMessage, SystemMessage

from agent.llm import get_llm
from agent.engine import AgentState

VERIFIER_PROMPT = """You are a result verifier. Given a user query and the execution results, assess whether the results are sufficient to answer the query.

User query: {query}
Execution plan:
{plan_summary}

Results:
{results_summary}

Output a JSON object with exactly these fields:
{{
  "is_sufficient": true/false,
  "gaps": ["list of missing information or issues, empty if sufficient"],
  "score": 0.0-1.0
}}

Rules:
- is_sufficient=true only if all key aspects of the query are addressed
- gaps should list specific missing information
- score: 0.0=useless, 0.5=partial, 1.0=complete
- Be strict but fair — don't demand perfection

Output ONLY the JSON, no other text."""


def _format_plan(plan: list) -> str:
    return "\n".join(f"- Step {t['id']}: {t['description']}" for t in plan)


def _format_results(step_results: list) -> str:
    lines = []
    for r in step_results:
        output_preview = r["output"][:200].replace("\n", " ")
        lines.append(f"- Step {r['task_id']} ({r['tool']}): {output_preview}")
    return "\n".join(lines) if lines else "No results yet."


async def verifier_node(state: AgentState) -> dict:
    llm = get_llm()
    query = state.query
    plan = state.plan
    step_results = state.step_results
    retry_count = state.retry_count

    prompt = VERIFIER_PROMPT.format(
        query=query,
        plan_summary=_format_plan(plan),
        results_summary=_format_results(step_results),
    )

    resp = await llm.ainvoke([
        SystemMessage(content=prompt),
        HumanMessage(content="Verify the results and output your assessment."),
    ])

    try:
        raw = resp.content.strip().removeprefix("```json").removesuffix("```").strip()
        result = json.loads(raw)
        verification = {
            "is_sufficient": result.get("is_sufficient", False),
            "gaps": result.get("gaps", []),
            "score": float(result.get("score", 0.0)),
        }
    except (json.JSONDecodeError, AttributeError):
        verification = {"is_sufficient": False, "gaps": ["Verification parsing failed"], "score": 0.0}

    return {
        "verification": verification,
        "retry_count": retry_count + 1,
    }
