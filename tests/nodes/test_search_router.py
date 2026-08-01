from uuid import uuid4

from backend.app.models.enums import SearchSource
from backend.app.models.search_query import SearchQuery
from backend.app.nodes.search_router import search_router_node


def test_search_router_routes_queries_by_source():
    search_queries = [
        SearchQuery(
            query="recent advances in artificial intelligence",
            sources=[SearchSource.WEB],
        ),
        SearchQuery(
            query="neural network architecture research",
            sources=[SearchSource.ARXIV],
        ),
    ]

    state = {
        "research_id": uuid4(),
        "topic": "Artificial Intelligence",
        "search_queries": search_queries,
    }

    result = search_router_node(state)

    assert len(result) == 2

    destinations = {send.node for send in result}

    assert destinations == {
        "web_search",
        "arxiv_search",
    }


def test_search_router_groups_queries_by_source():
    web_query_1 = SearchQuery(
        query="recent artificial intelligence advances",
        sources=[SearchSource.WEB],
    )
    web_query_2 = SearchQuery(
        query="AI applications in healthcare",
        sources=[SearchSource.WEB],
    )
    arxiv_query = SearchQuery(
        query="neural network architecture research",
        sources=[SearchSource.ARXIV],
    )

    state = {
        "search_queries": [
            web_query_1,
            web_query_2,
            arxiv_query,
        ],
    }

    result = search_router_node(state)

    sends = {
        send.node: send.arg["queries"]
        for send in result
    }

    assert sends["web_search"] == [
        web_query_1,
        web_query_2,
    ]

    assert sends["arxiv_search"] == [
        arxiv_query,
    ]


def test_search_router_sends_multi_source_query_to_each_source():
    query = SearchQuery(
        query="machine learning research applications",
        sources=[
            SearchSource.WEB,
            SearchSource.ARXIV,
            SearchSource.CROSSREF,
        ],
    )

    state = {
        "search_queries": [query],
    }

    result = search_router_node(state)

    sends = {
        send.node: send.arg["queries"]
        for send in result
    }

    assert set(sends) == {
        "web_search",
        "arxiv_search",
        "crossref_search",
    }

    assert sends["web_search"] == [query]
    assert sends["arxiv_search"] == [query]
    assert sends["crossref_search"] == [query]


def test_search_router_returns_empty_for_no_queries():
    state = {
        "search_queries": [],
    }

    result = search_router_node(state)

    assert result == []


def test_search_router_skips_invalid_query():
    valid_query = SearchQuery(
        query="artificial intelligence research",
        sources=[SearchSource.WEB],
    )

    state = {
        "search_queries": [
            "invalid query",
            valid_query,
        ],
    }

    result = search_router_node(state)

    assert len(result) == 1
    assert result[0].node == "web_search"
    assert result[0].arg["queries"] == [valid_query]