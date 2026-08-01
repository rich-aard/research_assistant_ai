from unittest.mock import Mock

import pytest

from backend.app.clients import tavily
from backend.app.models.enums import SearchSource


def test_get_tavily_client_is_cached(mocker):
    tavily.get_tavily_client.cache_clear()

    client = Mock()

    client_class = mocker.patch(
        "backend.app.clients.tavily.TavilyClient",
        return_value=client,
    )

    first = tavily.get_tavily_client()
    second = tavily.get_tavily_client()

    assert first is client
    assert second is client
    client_class.assert_called_once_with(
        api_key=tavily.settings.tavily_api_key,
    )

    tavily.get_tavily_client.cache_clear()


def test_search_web_success(mocker):
    response = {
        "results": [
            {
                "title": "Artificial Intelligence",
                "url": "https://example.com/ai",
                "content": "Artificial intelligence research.",
                "score": 0.95,
            },
            {
                "title": "Machine Learning",
                "url": "https://example.com/ml",
                "content": "Machine learning research.",
                "score": 0.85,
            },
        ]
    }

    client = Mock()
    client.search.return_value = response

    mocker.patch(
        "backend.app.clients.tavily.get_tavily_client",
        return_value=client,
    )

    results = tavily.search_web(
        "artificial intelligence",
        max_results=2,
    )

    assert len(results) == 2

    assert results[0].title == "Artificial Intelligence"
    assert str(results[0].url) == "https://example.com/ai"
    assert results[0].content == "Artificial intelligence research."
    assert results[0].source == SearchSource.WEB
    assert results[0].score == 0.95
    assert results[0].snippet == "Artificial intelligence research."

    assert results[1].title == "Machine Learning"
    assert results[1].source == SearchSource.WEB
    assert results[1].score == 0.85

    client.search.assert_called_once_with(
        query="artificial intelligence",
        max_results=2,
        include_answer=False,
        include_images=False,
    )


def test_search_web_empty_results(mocker):
    client = Mock()
    client.search.return_value = {"results": []}

    mocker.patch(
        "backend.app.clients.tavily.get_tavily_client",
        return_value=client,
    )

    results = tavily.search_web("artificial intelligence")

    assert results == []

    client.search.assert_called_once_with(
        query="artificial intelligence",
        max_results=5,
        include_answer=False,
        include_images=False,
    )


def test_search_web_missing_results_key(mocker):
    client = Mock()
    client.search.return_value = {}

    mocker.patch(
        "backend.app.clients.tavily.get_tavily_client",
        return_value=client,
    )

    results = tavily.search_web("machine learning")

    assert results == []


def test_search_web_missing_optional_item_fields(mocker):
    client = Mock()
    client.search.return_value = {
        "results": [
            {
                "title": "Artificial Intelligence",
                "url": "https://example.com/ai",
            }
        ]
    }

    mocker.patch(
        "backend.app.clients.tavily.get_tavily_client",
        return_value=client,
    )

    results = tavily.search_web("AI")

    assert len(results) == 1

    result = results[0]

    assert result.title == "Artificial Intelligence"
    assert str(result.url) == "https://example.com/ai"
    assert result.content == ""
    assert result.source == SearchSource.WEB
    assert result.score is None
    assert result.snippet is None


def test_search_web_failure(mocker):
    client = Mock()
    client.search.side_effect = RuntimeError("Tavily API unavailable")

    mocker.patch(
        "backend.app.clients.tavily.get_tavily_client",
        return_value=client,
    )

    with pytest.raises(
        RuntimeError,
        match="Tavily API unavailable",
    ):
        tavily.search_web("artificial intelligence")

    client.search.assert_called_once_with(
        query="artificial intelligence",
        max_results=5,
        include_answer=False,
        include_images=False,
    )


def test_search_web_default_max_results(mocker):
    client = Mock()
    client.search.return_value = {"results": []}

    mocker.patch(
        "backend.app.clients.tavily.get_tavily_client",
        return_value=client,
    )

    tavily.search_web("machine learning")

    client.search.assert_called_once_with(
        query="machine learning",
        max_results=5,
        include_answer=False,
        include_images=False,
    )
