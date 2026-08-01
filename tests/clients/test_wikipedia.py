from unittest.mock import Mock

import pytest

from backend.app.clients import wikipedia


def make_response(
    search_items: list[dict],
):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "query": {
            "search": search_items,
        }
    }
    return response


def test_get_wikipedia_session_is_cached(mocker):
    wikipedia.get_wikipedia_session.cache_clear()

    session = Mock()

    session_class = mocker.patch(
        "backend.app.clients.wikipedia.requests.Session",
        return_value=session,
    )

    first = wikipedia.get_wikipedia_session()
    second = wikipedia.get_wikipedia_session()

    assert first is session
    assert second is session

    session_class.assert_called_once()

    wikipedia.get_wikipedia_session.cache_clear()


def test_search_wikipedia_success(mocker):
    response = make_response(
        [
            {
                "pageid": 123,
                "title": "Artificial intelligence",
                "snippet": (
                    "Artificial intelligence is intelligence "
                    "demonstrated by machines."
                ),
            },
            {
                "pageid": 456,
                "title": "Machine learning",
                "snippet": (
                    "Machine learning is a field of study "
                    "in artificial intelligence."
                ),
            },
        ]
    )

    session = Mock()
    session.get.return_value = response

    mocker.patch(
        "backend.app.clients.wikipedia.get_wikipedia_session",
        return_value=session,
    )

    results = wikipedia.search_wikipedia(
        "artificial intelligence",
        max_results=2,
    )

    assert len(results) == 2

    assert results[0].title == "Artificial intelligence"
    assert (
        str(results[0].url)
        == "https://en.wikipedia.org/wiki/Artificial_intelligence"
    )
    assert (
        results[0].content
        == "Artificial intelligence is intelligence "
        "demonstrated by machines."
    )
    assert (
        results[0].snippet
        == "Artificial intelligence is intelligence "
        "demonstrated by machines."
    )
    assert results[0].source == "wikipedia"

    assert results[1].title == "Machine learning"
    assert results[1].source == "wikipedia"

    session.get.assert_called_once()

    _, kwargs = session.get.call_args

    assert kwargs["params"]["srsearch"] == "artificial intelligence"
    assert kwargs["params"]["srlimit"] == 2
    assert kwargs["params"]["format"] == "json"


def test_search_wikipedia_empty_results(mocker):
    response = make_response([])

    session = Mock()
    session.get.return_value = response

    mocker.patch(
        "backend.app.clients.wikipedia.get_wikipedia_session",
        return_value=session,
    )

    results = wikipedia.search_wikipedia(
        "artificial intelligence",
    )

    assert results == []

    session.get.assert_called_once()


def test_search_wikipedia_request_failure(mocker):
    session = Mock()

    error = wikipedia.requests.RequestException(
        "Wikipedia API unavailable"
    )

    session.get.side_effect = error

    mocker.patch(
        "backend.app.clients.wikipedia.get_wikipedia_session",
        return_value=session,
    )

    results = wikipedia.search_wikipedia(
        "artificial intelligence",
    )

    assert results == []

    session.get.assert_called_once()


def test_search_wikipedia_unexpected_failure(mocker):
    session = Mock()

    session.get.side_effect = RuntimeError(
        "Unexpected failure"
    )

    mocker.patch(
        "backend.app.clients.wikipedia.get_wikipedia_session",
        return_value=session,
    )

    with pytest.raises(
        RuntimeError,
        match="Unexpected failure",
    ):
        wikipedia.search_wikipedia(
            "artificial intelligence",
        )

    session.get.assert_called_once()


def test_search_wikipedia_skips_invalid_items(mocker):
    response = make_response(
        [
            {
                "pageid": 123,
                "title": "Artificial intelligence",
                "snippet": "AI summary.",
            },
            {
                "pageid": None,
                "title": "Invalid page",
                "snippet": "Should be skipped.",
            },
            {
                "pageid": 456,
                "title": None,
                "snippet": "Should also be skipped.",
            },
        ]
    )

    session = Mock()
    session.get.return_value = response

    mocker.patch(
        "backend.app.clients.wikipedia.get_wikipedia_session",
        return_value=session,
    )

    results = wikipedia.search_wikipedia(
        "artificial intelligence",
    )

    assert len(results) == 1
    assert results[0].title == "Artificial intelligence"