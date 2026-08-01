from unittest.mock import Mock

import httpx
import pytest

from backend.app.clients import crossref


def make_item(
    title: str = "Artificial Intelligence Research",
    url: str = "https://doi.org/10.1234/example",
):
    return {
        "title": [title],
        "URL": url,
    }


def test_get_crossref_client_is_cached(mocker):
    crossref.get_crossref_client.cache_clear()

    client = Mock()

    client_class = mocker.patch(
        "backend.app.clients.crossref.httpx.Client",
        return_value=client,
    )

    first = crossref.get_crossref_client()
    second = crossref.get_crossref_client()

    assert first is client
    assert second is client
    client_class.assert_called_once()

    crossref.get_crossref_client.cache_clear()


def test_search_crossref_success(mocker):
    item1 = make_item(
        title="Artificial Intelligence Research",
        url="https://doi.org/10.1234/ai",
    )

    item2 = make_item(
        title="Machine Learning Research",
        url="https://doi.org/10.5678/ml",
    )

    response = Mock()
    response.json.return_value = {
        "message": {
            "items": [item1, item2],
        },
    }

    client = Mock()
    client.get.return_value = response

    mocker.patch(
        "backend.app.clients.crossref.get_crossref_client",
        return_value=client,
    )

    results = crossref.search_crossref(
        "artificial intelligence",
        max_results=2,
    )

    assert len(results) == 2

    assert results[0].title == "Artificial Intelligence Research"
    assert str(results[0].url) == "https://doi.org/10.1234/ai"
    assert results[0].content == ""
    assert results[0].snippet == "Artificial Intelligence Research"
    assert results[0].source == "crossref"

    assert results[1].title == "Machine Learning Research"
    assert results[1].source == "crossref"

    client.get.assert_called_once_with(
        "",
        params={
            "query": "artificial intelligence",
            "rows": 2,
        },
    )

    response.raise_for_status.assert_called_once()


def test_search_crossref_empty_results(mocker):
    response = Mock()
    response.json.return_value = {
        "message": {
            "items": [],
        },
    }

    client = Mock()
    client.get.return_value = response

    mocker.patch(
        "backend.app.clients.crossref.get_crossref_client",
        return_value=client,
    )

    results = crossref.search_crossref(
        "artificial intelligence",
    )

    assert results == []

    client.get.assert_called_once()
    response.raise_for_status.assert_called_once()


def test_search_crossref_http_failure(mocker):
    response = Mock()

    error = httpx.HTTPStatusError(
        "Crossref API unavailable",
        request=Mock(),
        response=Mock(),
    )

    response.raise_for_status.side_effect = error

    client = Mock()
    client.get.return_value = response

    mocker.patch(
        "backend.app.clients.crossref.get_crossref_client",
        return_value=client,
    )

    results = crossref.search_crossref(
        "artificial intelligence",
    )

    assert results == []

    client.get.assert_called_once()
    response.raise_for_status.assert_called_once()


def test_search_crossref_request_failure(mocker):
    client = Mock()

    error = httpx.RequestError(
        "Connection failed",
        request=Mock(),
    )

    client.get.side_effect = error

    mocker.patch(
        "backend.app.clients.crossref.get_crossref_client",
        return_value=client,
    )

    results = crossref.search_crossref(
        "artificial intelligence",
    )

    assert results == []

    client.get.assert_called_once()


def test_search_crossref_unexpected_failure(mocker):
    client = Mock()
    client.get.side_effect = RuntimeError(
        "Unexpected error",
    )

    mocker.patch(
        "backend.app.clients.crossref.get_crossref_client",
        return_value=client,
    )

    with pytest.raises(
        RuntimeError,
        match="Unexpected error",
    ):
        crossref.search_crossref(
            "artificial intelligence",
        )

    client.get.assert_called_once()


def test_search_crossref_default_max_results(mocker):
    response = Mock()
    response.json.return_value = {
        "message": {
            "items": [],
        },
    }

    client = Mock()
    client.get.return_value = response

    mocker.patch(
        "backend.app.clients.crossref.get_crossref_client",
        return_value=client,
    )

    crossref.search_crossref("machine learning")

    client.get.assert_called_once_with(
        "",
        params={
            "query": "machine learning",
            "rows": 5,
        },
    )
