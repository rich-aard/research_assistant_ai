from langgraph.graph import END, START, StateGraph

from backend.app.models.state import ResearchState
from backend.app.nodes.planner import planner_node


def build_graph():
    workflow = StateGraph(ResearchState)

    # nodes
    workflow.add_node(
        "planner",
        planner_node,
    )

    # edges
    workflow.add_edge(
        START,
        "planner",
    )
    workflow.add_edge("planner", END)

    return workflow.compile()
