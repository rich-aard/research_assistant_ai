import pytest

from backend.app.models.enums import SearchSource
from backend.app.models.search import SearchResult
from backend.app.models.search_query import SearchQuery
from backend.app.nodes.crossref_search import crossref_search_node


def make_search_query(
    query: str = "artificial intelligence",
) -> SearchQuery:
    return SearchQuery(
        query=query,
        sources=[SearchSource.CROSSREF],
    )


def make_result(
    title: str = "Artificial Intelligence Research",
) -> SearchResult:
    return SearchResult(
        title=title,
        url="https://doi.org/10.1234/example",
        content="Research content.",
        source=SearchSource.CROSSREF,
        score=None,
        snippet=title,
    )


@pytest.mark.asyncio
async def test_crossref_search_node_success(mocker):
    query1 = make_search_query(
        "artificial intelligence",
    )
    query2 = make_search_query(
        "machine learning",
    )

    result1 = make_result(
        "Artificial Intelligence Research",
    )
    result2 = make_result(
        "Machine Learning Research",
    )

    mock_search = mocker.patch(
        "backend.app.nodes.crossref_search.search_crossref",
        side_effect=[
            [result1],
            [result2],
        ],
    )

    result = await crossref_search_node(
        {
            "queries": [query1, query2],
        }
    )

    assert result == {
        "crossref_results": [result1, result2],
    }

    assert mock_search.call_count == 2

    mock_search.assert_any_call(
        "artificial intelligence",
    )
    mock_search.assert_any_call(
        "machine learning",
    )


@pytest.mark.asyncio
async def test_crossref_search_node_empty_queries(mocker):
    mock_search = mocker.patch(
        "backend.app.nodes.crossref_search.search_crossref",
    )

    result = await crossref_search_node(
        {
            "queries": [],
        }
    )

    assert result == {
        "crossref_results": [],
    }

    mock_search.assert_not_called()


@pytest.mark.asyncio
async def test_crossref_search_node_missing_queries(mocker):
    mock_search = mocker.patch(
        "backend.app.nodes.crossref_search.search_crossref",
    )

    result = await crossref_search_node({})

    assert result == {
        "crossref_results": [],
    }

    mock_search.assert_not_called()


@pytest.mark.asyncio
async def test_crossref_search_node_partial_failure(mocker):
    query1 = make_search_query(
        "artificial intelligence",
    )
    query2 = make_search_query(
        "machine learning",
    )

    successful_result = make_result(
        "Machine Learning Research",
    )

    mock_search = mocker.patch(
        "backend.app.nodes.crossref_search.search_crossref",
        side_effect=[
            RuntimeError("Crossref unavailable"),
            [successful_result],
        ],
    )

    result = await crossref_search_node(
        {
            "queries": [query1, query2],
        }
    )

    assert result == {
        "crossref_results": [successful_result],
    }

    assert mock_search.call_count == 2


@pytest.mark.asyncio
async def test_crossref_search_node_all_fail(mocker):
    query1 = make_search_query(
        "artificial intelligence",
    )
    query2 = make_search_query(
        "machine learning",
    )

    mock_search = mocker.patch(
        "backend.app.nodes.crossref_search.search_crossref",
        side_effect=RuntimeError("Crossref unavailable"),
    )

    result = await crossref_search_node(
        {
            "queries": [query1, query2],
        }
    )

    assert result == {
        "crossref_results": [],
    }

    assert mock_search.call_count == 2


@pytest.mark.asyncio
async def test_crossref_search_node_skips_invalid_query(mocker):
    valid_query = make_search_query(
        "machine learning",
    )

    successful_result = make_result(
        "Machine Learning Research",
    )

    mock_search = mocker.patch(
        "backend.app.nodes.crossref_search.search_crossref",
        return_value=[successful_result],
    )

    result = await crossref_search_node(
        {
            "queries": [
                "invalid query",
                valid_query,
            ],
        }
    )

    assert result == {
        "crossref_results": [successful_result],
    }

    mock_search.assert_called_once_with(
        "machine learning",
    )
