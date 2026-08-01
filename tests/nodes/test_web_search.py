import pytest

from backend.app.models.enums import SearchSource
from backend.app.models.search import SearchResult
from backend.app.models.search_query import SearchQuery
from backend.app.nodes.web_search import web_search_node


def make_search_query(
    query: str,
) -> SearchQuery:
    return SearchQuery(
        query=query,
        sources=[SearchSource.WEB],
    )


def make_search_result(
    title: str = "AI Research",
    source: SearchSource = SearchSource.WEB,
    url: str = "https://example.com",
    content: str = "Research content.",
) -> SearchResult:
    return SearchResult(
        title=title,
        source=source,
        url=url,
        content=content,
    )


@pytest.mark.asyncio
async def test_web_search_node_success(mocker):
    results = [
        make_search_result(
            title="AI Research",
            url="https://example.com/ai",
        ),
        make_search_result(
            title="Machine Learning",
            url="https://example.com/ml",
        ),
    ]

    mock_search = mocker.patch(
        "backend.app.nodes.web_search.search_web",
        side_effect=[
            [results[0]],
            [results[1]],
        ],
    )

    state = {
        "queries": [
            make_search_query(
                "artificial intelligence research",
            ),
            make_search_query(
                "machine learning research",
            ),
        ],
    }

    result = await web_search_node(state)

    assert result["web_results"] == results
    assert mock_search.call_count == 2

    mock_search.assert_any_call(
        "artificial intelligence research",
    )
    mock_search.assert_any_call(
        "machine learning research",
    )


@pytest.mark.asyncio
async def test_web_search_node_empty_queries(mocker):
    mock_search = mocker.patch(
        "backend.app.nodes.web_search.search_web",
    )

    result = await web_search_node(
        {
            "queries": [],
        }
    )

    assert result == {
        "web_results": [],
    }

    mock_search.assert_not_called()


@pytest.mark.asyncio
async def test_web_search_node_missing_queries(mocker):
    mock_search = mocker.patch(
        "backend.app.nodes.web_search.search_web",
    )

    result = await web_search_node({})

    assert result == {
        "web_results": [],
    }

    mock_search.assert_not_called()


@pytest.mark.asyncio
async def test_web_search_node_partial_failure(mocker):
    successful_result = make_search_result()

    mock_search = mocker.patch(
        "backend.app.nodes.web_search.search_web",
        side_effect=[
            [successful_result],
            RuntimeError("Tavily failed"),
        ],
    )

    result = await web_search_node(
        {
            "queries": [
                make_search_query("successful query"),
                make_search_query("failing query"),
            ],
        }
    )

    assert result["web_results"] == [successful_result]

    assert mock_search.call_count == 2

    mock_search.assert_any_call("successful query")
    mock_search.assert_any_call("failing query")


@pytest.mark.asyncio
async def test_web_search_node_all_fail(mocker):
    mock_search = mocker.patch(
        "backend.app.nodes.web_search.search_web",
        side_effect=RuntimeError("Tavily failed"),
    )

    result = await web_search_node(
        {
            "queries": [
                make_search_query("query one"),
                make_search_query("query two"),
            ],
        }
    )

    assert result == {
        "web_results": [],
    }

    assert mock_search.call_count == 2


@pytest.mark.asyncio
async def test_web_search_node_skips_invalid_query(mocker):
    mock_search = mocker.patch(
        "backend.app.nodes.web_search.search_web",
        return_value=[],
    )

    result = await web_search_node(
        {
            "queries": [
                "invalid query",
                make_search_query("valid query"),
            ],
        }
    )

    assert result == {
        "web_results": [],
    }

    mock_search.assert_called_once_with("valid query")
