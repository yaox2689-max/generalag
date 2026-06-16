from langchain_core.messages import HumanMessage, SystemMessage

from agent.llm import get_llm
from agent.state import AgentState

WRITER_PROMPT = """You are a professional answer writer. Given a user query and the execution results, write a clear, well-structured final answer.

User query: {query}
Domain: {domain}

Execution results:
{results}

Instructions:
- Write in the same language as the user's query
- Structure the answer with clear sections (use markdown headers if needed)
- Include specific data and numbers from the results
- If the results contain sources or references, cite them
- Be concise but thorough — aim for completeness without fluff
- If the data is insufficient, acknowledge what you can and cannot answer"""


def _format_results(step_results: list) -> str:
    lines = []
    for r in step_results:
        lines.append(f"### Step {r['task_id']} ({r['tool']})\n{r['output']}")
    return "\n\n".join(lines) if lines else "No results available."


async def writer_node(state: AgentState) -> dict:
    llm = get_llm(temperature=0.3)
    query = state["query"]
    domain = state.get("domain", "general")
    step_results = state.get("step_results", [])

    prompt = WRITER_PROMPT.format(
        query=query,
        domain=domain,
        results=_format_results(step_results),
    )

    resp = await llm.ainvoke([
        SystemMessage(content=prompt),
        HumanMessage(content="Write the final answer now."),
    ])

    # Collect sources from step results
    sources = []
    for r in step_results:
        tool = r.get("tool", "")
        if tool in ("rag_search", "web_search", "financial_report"):
            sources.append(f"[{tool}] Step {r['task_id']}")

    return {
        "final_answer": resp.content,
        "sources": sources,
    }
