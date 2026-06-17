from langchain_core.messages import HumanMessage, SystemMessage

from agent.llm import get_llm
from agent.engine import AgentState

DOMAIN_KEYWORDS = {
    "finance": ["财报", "利润", "营收", "股价", "股票", "基金", "PE", "ROE", "净利", "毛利", "营收", "资产", "负债", "现金流", "市值", "分红", "市盈率"],
    "qa": ["什么是", "解释", "定义", "原理", "区别"],
    "tech": ["编程", "代码", "算法", "框架", "API", "Python", "Java", "数据库", "Linux", "Docker"],
    "science": ["物理", "化学", "生物", "数学定理", "实验", "量子", "相对论"],
    "daily": ["天气", "怎么做", "推荐", "食谱", "路线", "翻译"],
}

SIMPLE_KEYWORDS = ["今天", "最新", "现在", "多少", "是什么"]


def rule_based_route(query: str) -> tuple[str, str, float] | None:
    """Rule layer: fast routing for clear-cut cases. Returns (domain, complexity, confidence)."""
    query_lower = query.lower()

    domain = None
    matched_keywords = 0
    for dom, keywords in DOMAIN_KEYWORDS.items():
        matches = sum(1 for kw in keywords if kw in query_lower)
        if matches > 0:
            domain = dom
            matched_keywords = matches
            break

    if not domain:
        return None

    # Confidence based on: keyword matches + query brevity
    confidence = min(0.95, 0.7 + matched_keywords * 0.1)

    # Single-domain + simple keyword → fast path
    if any(kw in query_lower for kw in SIMPLE_KEYWORDS):
        return domain, "simple", confidence

    # Single-domain, short query → still simple
    if domain and len(query) < 30:
        return domain, "simple", confidence

    return None


async def llm_based_route(query: str) -> tuple[str, str, float]:
    """LLM layer: structured routing for ambiguous cases."""
    llm = get_llm()

    system_prompt = """You are a routing classifier. Given a user query, output a JSON object with exactly three fields:
- "domain": one of "finance", "qa", "tech", "science", "daily", "general"
- "complexity": one of "simple", "complex"
- "confidence": a float between 0.0 and 1.0

Rules:
- "finance": stocks, financial reports, company analysis, market data
- "qa": factual questions with a single definitive answer
- "tech": programming, software, technical questions
- "science": scientific concepts, experiments, theories
- "daily": everyday life, recipes, recommendations, translations
- "general": everything else
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
        confidence = float(result.get("confidence", 0.5))
        valid_domains = ("finance", "qa", "tech", "science", "daily", "general")
        if domain not in valid_domains:
            domain = "general"
        if complexity not in ("simple", "complex"):
            complexity = "complex"
        confidence = max(0.0, min(1.0, confidence))
        return domain, complexity, confidence
    except (json.JSONDecodeError, AttributeError):
        return "general", "complex", 0.3


async def router_node(state: AgentState) -> dict:
    query = state.query

    # Try rule-based first
    route = rule_based_route(query)
    if route:
        domain, complexity, confidence = route
    else:
        # Fall back to LLM
        domain, complexity, confidence = await llm_based_route(query)

    # Low confidence → default to complex (safer)
    if confidence < 0.7:
        complexity = "complex"

    return {"domain": domain, "complexity": complexity}
