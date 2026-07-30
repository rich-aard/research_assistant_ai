import pytest

from backend.app.models.search import SearchResult
from backend.app.nodes.merge_documents import (
    _deduplicate_documents,
    merge_documents_node,
)


def make_search_result(
    title: str = "AI Research",
    source: str = "tavily",
    url: str = "https://example.com",
    content: str = "Research content.",
    score: float | None = 0.5,
) -> SearchResult:
    return SearchResult(
        title=title,
        source=source,
        url=url,
        content=content,
        score=score,
    )


def test_deduplicate_documents():
    first = make_search_result(
        title="First",
        url="https://example.com/shared",
        score=0.5,
    )

    duplicate = make_search_result(
        title="Duplicate",
        url="https://example.com/shared",
        score=0.9,
    )

    second = make_search_result(
        title="Second",
        url="https://example.com/second",
        score=0.7,
    )

    result = _deduplicate_documents(
        [first, duplicate, second]
    )

    assert result == [first, second]


def test_deduplicate_documents_empty():
    result = _deduplicate_documents([])

    assert result == []


@pytest.mark.asyncio
async def test_merge_documents_node_success():
    web_results = [
        make_search_result(
            title="Web Low",
            url="https://example.com/low",
            score=0.3,
        ),
        make_search_result(
            title="Web High",
            url="https://example.com/high",
            score=0.9,
        ),
    ]

    arxiv_results = [
        make_search_result(
            title="Academic",
            source="arxiv",
            url="https://arxiv.org/1234",
            score=0.7,
        ),
    ]

    result = await merge_documents_node(
        {
            "web_results": web_results,
            "arxiv_results": arxiv_results,
        }
    )

    assert result["merged_documents"] == [
        web_results[1],
        arxiv_results[0],
        web_results[0],
    ]


@pytest.mark.asyncio
async def test_merge_documents_node_deduplicates():
    web_result = make_search_result(
        title="Web Result",
        url="https://example.com/shared",
        score=0.5,
    )

    arxiv_result = make_search_result(
        title="Duplicate Result",
        source="arxiv",
        url="https://example.com/shared",
        score=0.9,
    )

    result = await merge_documents_node(
        {
            "web_results": [web_result],
            "arxiv_results": [arxiv_result],
        }
    )

    assert len(result["merged_documents"]) == 1
    assert result["merged_documents"][0] == web_result


@pytest.mark.asyncio
async def test_merge_documents_node_empty():
    result = await merge_documents_node(
        {
            "web_results": [],
            "arxiv_results": [],
        }
    )

    assert result == {
        "merged_documents": [],
    }


@pytest.mark.asyncio
async def test_merge_documents_node_missing_results():
    result = await merge_documents_node({})

    assert result == {
        "merged_documents": [],
    }


@pytest.mark.asyncio
async def test_merge_documents_node_limits_to_ten():
    documents = [
        make_search_result(
            title=f"Document {i}",
            url=f"https://example.com/{i}",
            score=float(i),
        )
        for i in range(15)
    ]

    result = await merge_documents_node(
        {
            "web_results": documents,
            "arxiv_results": [],
        }
    )

    assert len(result["merged_documents"]) == 10

    # Highest scores should be retained.
    assert [
        document.title
        for document in result["merged_documents"]
    ] == [
        "Document 14",
        "Document 13",
        "Document 12",
        "Document 11",
        "Document 10",
        "Document 9",
        "Document 8",
        "Document 7",
        "Document 6",
        "Document 5",
    ]


@pytest.mark.asyncio
async def test_merge_documents_node_none_scores():
    documents = [
        make_search_result(
            title="No Score",
            url="https://example.com/no-score",
            score=None,
        ),
        make_search_result(
            title="Scored",
            url="https://example.com/scored",
            score=0.8,
        ),
    ]

    result = await merge_documents_node(
        {
            "web_results": documents,
            "arxiv_results": [],
        }
    )

    assert result["merged_documents"] == [
        documents[1],
        documents[0],
    ]