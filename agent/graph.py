from langgraph.graph import END, StateGraph

from agent.state import AgentState


def router_node(state: AgentState) -> dict:
    raise NotImplementedError("Router node not yet implemented")


def planner_node(state: AgentState) -> dict:
    raise NotImplementedError("Planner node not yet implemented")


def executor_node(state: AgentState) -> dict:
    raise NotImplementedError("Executor node not yet implemented")


def verifier_node(state: AgentState) -> dict:
    raise NotImplementedError("Verifier node not yet implemented")


def writer_node(state: AgentState) -> dict:
    raise NotImplementedError("Writer node not yet implemented")


def route_after_router(state: AgentState) -> str:
    if state.get("complexity") == "simple":
        return "executor"
    return "planner"


def route_after_verifier(state: AgentState) -> str:
    if state.get("retry_count", 0) >= 3:
        return "writer"
    verification = state.get("verification", {})
    if verification.get("is_sufficient", False):
        return "writer"
    return "planner"


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("router", router_node)
    graph.add_node("planner", planner_node)
    graph.add_node("executor", executor_node)
    graph.add_node("verifier", verifier_node)
    graph.add_node("writer", writer_node)

    graph.set_entry_point("router")

    graph.add_conditional_edges("router", route_after_router, {
        "executor": "executor",
        "planner": "planner",
    })

    graph.add_edge("planner", "executor")
    graph.add_edge("executor", "verifier")

    graph.add_conditional_edges("verifier", route_after_verifier, {
        "writer": "writer",
        "planner": "planner",
    })

    graph.add_edge("writer", END)

    return graph
