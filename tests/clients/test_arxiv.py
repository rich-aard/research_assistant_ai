from unittest.mock import Mock

import pytest

from backend.app.clients import arxiv


def make_paper(
    title: str = "Artificial Intelligence Research",
    entry_id: str = "https://arxiv.org/abs/1234.5678",
    summary: str = "Research about artificial intelligence.",
):
    paper = Mock()
    paper.title = title
    paper.entry_id = entry_id
    paper.summary = summary
    return paper


def test_get_arxiv_client_is_cached(mocker):
    arxiv.get_arxiv_client.cache_clear()

    client = Mock()

    client_class = mocker.patch(
        "backend.app.clients.arxiv.Client",
        return_value=client,
    )

    first = arxiv.get_arxiv_client()
    second = arxiv.get_arxiv_client()

    assert first is client
    assert second is client
    client_class.assert_called_once()

    arxiv.get_arxiv_client.cache_clear()


def test_search_arxiv_success(mocker):
    paper1 = make_paper(
        title="Artificial Intelligence Research",
        entry_id="https://arxiv.org/abs/1234.5678",
        summary="AI research summary.",
    )

    paper2 = make_paper(
        title="Machine Learning Research",
        entry_id="https://arxiv.org/abs/2345.6789",
        summary="Machine learning research summary.",
    )

    client = Mock()
    client.results.return_value = [paper1, paper2]

    mocker.patch(
        "backend.app.clients.arxiv.get_arxiv_client",
        return_value=client,
    )

    results = arxiv.search_arxiv(
        "artificial intelligence",
        max_results=2,
    )

    assert len(results) == 2

    assert results[0].title == "Artificial Intelligence Research"
    assert str(results[0].url) == "https://arxiv.org/abs/1234.5678"
    assert results[0].content == "AI research summary."
    assert results[0].snippet == "AI research summary."
    assert results[0].source == "arxiv"

    assert results[1].title == "Machine Learning Research"
    assert results[1].source == "arxiv"

    client.results.assert_called_once()

    search = client.results.call_args.args[0]

    assert search.query == "artificial intelligence"
    assert search.max_results == 2


def test_search_arxiv_empty_results(mocker):
    client = Mock()
    client.results.return_value = []

    mocker.patch(
        "backend.app.clients.arxiv.get_arxiv_client",
        return_value=client,
    )

    results = arxiv.search_arxiv("artificial intelligence")

    assert results == []

    client.results.assert_called_once()


def test_search_arxiv_failure(mocker):
    client = Mock()
    error = RuntimeError("arXiv API unavailable")
    client.results.side_effect = error

    mocker.patch(
        "backend.app.clients.arxiv.get_arxiv_client",
        return_value=client,
    )

    with pytest.raises(RuntimeError, match="arXiv API unavailable"):
        arxiv.search_arxiv("artificial intelligence")

    client.results.assert_called_once()


def test_search_arxiv_default_max_results(mocker):
    client = Mock()
    client.results.return_value = []

    mocker.patch(
        "backend.app.clients.arxiv.get_arxiv_client",
        return_value=client,
    )

    arxiv.search_arxiv("machine learning")

    search = client.results.call_args.args[0]

    assert search.query == "machine learning"
    assert search.max_results == 5
