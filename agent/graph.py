from langgraph.graph import END, StateGraph

from agent.executor import executor_node
from agent.planner import planner_node
from agent.router import router_node
from agent.state import AgentState
from agent.verifier import verifier_node
from agent.writer import writer_node


def route_after_router(state: AgentState) -> str:
    if state.get("complexity") == "simple":
        return "executor"
    return "planner"


def route_after_executor(state: AgentState) -> str:
    if state.get("complexity") == "simple":
        return "writer"
    return "verifier"


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

    graph.add_conditional_edges("executor", route_after_executor, {
        "writer": "writer",
        "verifier": "verifier",
    })

    graph.add_conditional_edges("verifier", route_after_verifier, {
        "writer": "writer",
        "planner": "planner",
    })

    graph.add_edge("writer", END)

    return graph


def compile_graph():
    graph = build_graph()
    return graph.compile()
