from langchain_core.messages import HumanMessage, SystemMessage

from agent.llm import get_llm
from agent.state import AgentState

DOMAIN_KEYWORDS = {
    "finance": ["财报", "利润", "营收", "股价", "股票", "基金", "PE", "ROE", "净利", "毛利", "营收", "资产", "负债", "现金流"],
    "qa": ["什么是", "解释", "定义", "原理", "区别"],
}

SIMPLE_KEYWORDS = ["今天", "最新", "现在", "多少", "是什么"]


def rule_based_route(query: str) -> tuple[str, str] | None:
    """Rule layer: fast routing for clear-cut cases."""
    query_lower = query.lower()

    domain = None
    for dom, keywords in DOMAIN_KEYWORDS.items():
        if any(kw in query_lower for kw in keywords):
            domain = dom
            break

    # Single-domain + simple keyword → fast path
    if domain and any(kw in query_lower for kw in SIMPLE_KEYWORDS):
        return domain, "simple"

    # Single-domain, short query → still simple
    if domain and len(query) < 30:
        return domain, "simple"

    return None


async def llm_based_route(query: str) -> tuple[str, str]:
    """LLM layer: structured routing for ambiguous cases."""
    llm = get_llm()

    system_prompt = """You are a routing classifier. Given a user query, output a JSON object with exactly two fields:
- "domain": one of "finance", "qa", "general"
- "complexity": one of "simple", "complex"

Rules:
- "finance": questions about stocks, financial reports, company analysis, market data
- "qa": factual questions with a single definitive answer
- "general": everything else (multi-step analysis, comparisons, recommendations)
- "simple": can be answered with a single tool call or direct lookup
- "complex": requires multiple steps, comparison, or analysis

Output ONLY the JSON object, no other text."""

    resp = await llm.ainvoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Query: {query}"),
    ])

    import json
    try:
        result = json.loads(resp.content.strip().removeprefix("```json").removesuffix("```").strip())
        domain = result.get("domain", "general")
        complexity = result.get("complexity", "complex")
        if domain not in ("finance", "qa", "general"):
            domain = "general"
        if complexity not in ("simple", "complex"):
            complexity = "complex"
        return domain, complexity
    except (json.JSONDecodeError, AttributeError):
        return "general", "complex"


async def router_node(state: AgentState) -> dict:
    query = state["query"]

    # Try rule-based first
    route = rule_based_route(query)
    if route:
        domain, complexity = route
    else:
        # Fall back to LLM
        domain, complexity = await llm_based_route(query)

    return {"domain": domain, "complexity": complexity}
