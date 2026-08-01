from unittest.mock import Mock

from backend.app.models.enums import SearchSource
from backend.app.models.search import SearchResult
from backend.app.models.search_query import SearchQuery
from backend.app.nodes.wikipedia_search import wikipedia_search_node


def make_search_query(query: str) -> SearchQuery:
    return SearchQuery(
        query=query,
        sources=[SearchSource.WIKIPEDIA],
    )


def test_wikipedia_search_node_success(mocker):
    result1 = SearchResult(
        title="Artificial Intelligence",
        url="https://en.wikipedia.org/wiki/Artificial_intelligence",
        content="Artificial intelligence is intelligence demonstrated by machines.",
        source="wikipedia",
        score=0.9,
    )

    result2 = SearchResult(
        title="Machine Learning",
        url="https://en.wikipedia.org/wiki/Machine_learning",
        content="Machine learning is a branch of artificial intelligence.",
        source="wikipedia",
        score=0.8,
    )

    mock_search = mocker.patch(
        "backend.app.nodes.wikipedia_search.search_wikipedia",
        side_effect=[
            [result1],
            [result2],
        ],
    )

    result = wikipedia_search_node(
        {
            "queries": [
                make_search_query("artificial intelligence"),
                make_search_query("machine learning"),
            ],
        }
    )

    assert result == {
        "wikipedia_results": [
            result1,
            result2,
        ],
    }

    assert mock_search.call_count == 2

    mock_search.assert_any_call(
        "artificial intelligence",
    )
    mock_search.assert_any_call(
        "machine learning",
    )

def test_wikipedia_search_node_empty_queries(mocker):
    mock_search = mocker.patch(
        "backend.app.nodes.wikipedia_search.search_wikipedia",
    )

    result = wikipedia_search_node(
        {
            "queries": [],
        }
    )

    assert result == {
        "wikipedia_results": [],
    }

    mock_search.assert_not_called()

def test_wikipedia_search_node_missing_queries(mocker):
    mock_search = mocker.patch(
        "backend.app.nodes.wikipedia_search.search_wikipedia",
    )

    result = wikipedia_search_node({})

    assert result == {
        "wikipedia_results": [],
    }

    mock_search.assert_not_called()

def test_wikipedia_search_node_partial_failure(mocker):
    successful_result = SearchResult(
        title="Machine Learning",
        url="https://en.wikipedia.org/wiki/Machine_learning",
        content="Machine learning is a branch of artificial intelligence.",
        source="wikipedia",
        score=0.8,
    )

    mock_search = mocker.patch(
        "backend.app.nodes.wikipedia_search.search_wikipedia",
        side_effect=[
            RuntimeError("Wikipedia unavailable"),
            [successful_result],
        ],
    )

    result = wikipedia_search_node(
        {
            "queries": [
                make_search_query("artificial intelligence"),
                make_search_query("machine learning"),
            ],
        }
    )

    assert result == {
        "wikipedia_results": [
            successful_result,
        ],
    }

    assert mock_search.call_count == 2

def test_wikipedia_search_node_all_fail(mocker):
    mock_search = mocker.patch(
        "backend.app.nodes.wikipedia_search.search_wikipedia",
        side_effect=RuntimeError("Wikipedia unavailable"),
    )

    result = wikipedia_search_node(
        {
            "queries": [
                make_search_query("query one"),
                make_search_query("query two"),
            ],
        }
    )

    assert result == {
        "wikipedia_results": [],
    }

    assert mock_search.call_count == 2


def test_wikipedia_search_node_skips_invalid_query(mocker):
    mock_search = mocker.patch(
        "backend.app.nodes.wikipedia_search.search_wikipedia",
        return_value=[],
    )

    result = wikipedia_search_node(
        {
            "queries": [
                Mock(),
                make_search_query("artificial intelligence"),
            ],
        }
    )

    assert result == {
        "wikipedia_results": [],
    }

    mock_search.assert_called_once_with(
        "artificial intelligence",
    )