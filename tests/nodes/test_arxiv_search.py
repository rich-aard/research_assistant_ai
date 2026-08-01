import pytest

from backend.app.models.search import SearchResult
from backend.app.nodes.arxiv_search import arxiv_search_node


def make_search_result(
    title: str = "Attention Is All You Need",
    source: str = "arxiv",
    url: str = "https://arxiv.org/abs/1706.03762",
    content: str = "Transformer architecture research.",
) -> SearchResult:
    return SearchResult(
        title=title,
        source=source,
        url=url,
        content=content,
    )


@pytest.mark.asyncio
async def test_arxiv_search_node_success(mocker):
    results_1 = [
        make_search_result(
            title="Paper One",
            url="https://arxiv.org/abs/1111.1111",
        )
    ]

    results_2 = [
        make_search_result(
            title="Paper Two",
            url="https://arxiv.org/abs/2222.2222",
        ),
        make_search_result(
            title="Paper Three",
            url="https://arxiv.org/abs/3333.3333",
        ),
    ]

    mock_search = mocker.patch(
        "backend.app.nodes.arxiv_search.search_arxiv",
        side_effect=[results_1, results_2],
    )

    state = {
        "queries": [
            "transformer architecture",
            "large language model attention",
        ],
    }

    result = await arxiv_search_node(state)

    assert result["arxiv_results"] == results_1 + results_2

    assert mock_search.call_count == 2
    mock_search.assert_any_call(
        "transformer architecture",
        max_results=3,
    )
    mock_search.assert_any_call(
        "large language model attention",
        max_results=3,
    )


@pytest.mark.asyncio
async def test_arxiv_search_node_empty_queries(caplog):
    result = await arxiv_search_node(
        {
            "queries": [],
        }
    )

    assert result == {
        "arxiv_results": [],
    }


@pytest.mark.asyncio
async def test_arxiv_search_node_missing_queries():
    result = await arxiv_search_node({})

    assert result == {
        "arxiv_results": [],
    }


@pytest.mark.asyncio
async def test_arxiv_search_node_partial_failure(mocker):
    successful_results = [
        make_search_result(
            title="Successful Paper",
        )
    ]

    mocker.patch(
        "backend.app.nodes.arxiv_search.search_arxiv",
        side_effect=[
            RuntimeError("arXiv unavailable"),
            successful_results,
        ],
    )

    result = await arxiv_search_node(
        {
            "queries": [
                "failed query",
                "successful query",
            ],
        }
    )

    assert result["arxiv_results"] == successful_results


@pytest.mark.asyncio
async def test_arxiv_search_node_all_fail(mocker):
    mocker.patch(
        "backend.app.nodes.arxiv_search.search_arxiv",
        side_effect=RuntimeError("arXiv unavailable"),
    )

    result = await arxiv_search_node(
        {
            "queries": [
                "query one",
                "query two",
            ],
        }
    )

    assert result == {
        "arxiv_results": [],
    }