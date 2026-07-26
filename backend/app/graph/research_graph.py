from langgraph.graph import END, START, StateGraph

from backend.app.models.state import ResearchState
from backend.app.nodes.arxiv_search import arxiv_search_node
from backend.app.nodes.planner import planner_node
from backend.app.nodes.web_search import web_search_node


def build_graph():
    """
    Build and compile the research workflow graph.
    """
    workflow = StateGraph(ResearchState)

    # nodes
    workflow.add_node(
        "planner",
        planner_node,
    )
    workflow.add_node(
        "web_search",
        web_search_node,
    )
    workflow.add_node("arxiv_search", arxiv_search_node)

    # edges
    workflow.add_edge(
        START,
        "planner",
    )
    workflow.add_edge(
        "planner",
        "web_search",
    )

    workflow.add_edge(
        "web_search", 
        "arxiv_search"
        )
    workflow.add_edge(
        "arxiv_search", 
        END
        )

    return workflow.compile()
