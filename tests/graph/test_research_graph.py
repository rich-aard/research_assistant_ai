from langgraph.graph import END, START

from backend.app.graph.research_graph import build_graph


def test_build_graph():
    graph = build_graph()

    assert graph is not None


def test_graph_contains_all_nodes():
    graph = build_graph()

    nodes = graph.nodes

    expected_nodes = {
        "planner",
        "query_generator",
        "web_search",
        "arxiv_search",
        "merge_documents",
        "writer",
        "summarizer",
    }

    assert expected_nodes.issubset(nodes.keys())


def test_graph_start_and_end():
    graph = build_graph()

    assert START in graph.get_graph().nodes
    assert END in graph.get_graph().nodes


def test_graph_edges():
    graph = build_graph()
    edges = graph.get_graph().edges

    edge_pairs = {
        (edge.source, edge.target)
        for edge in edges
    }

    expected_edges = {
        (START, "planner"),
        ("planner", "query_generator"),
        ("query_generator", "web_search"),
        ("query_generator", "arxiv_search"),
        ("web_search", "merge_documents"),
        ("arxiv_search", "merge_documents"),
        ("merge_documents", "writer"),
        ("writer", "summarizer"),
        ("summarizer", END),
    }

    assert expected_edges.issubset(edge_pairs)