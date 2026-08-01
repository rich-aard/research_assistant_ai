import pytest

from backend.app.models.enums import SearchSource
from backend.app.models.search import SearchResult
from backend.app.nodes.merge_documents import (
    _deduplicate_documents,
    merge_documents_node,
)


def make_search_result(
    title: str = "AI Research",
    source: SearchSource = SearchSource.WEB,
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
        [first, duplicate, second],
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
            source=SearchSource.WEB,
            url="https://example.com/web-low",
            score=0.3,
        ),
        make_search_result(
            title="Web High",
            source=SearchSource.WEB,
            url="https://example.com/web-high",
            score=0.9,
        ),
    ]

    arxiv_results = [
        make_search_result(
            title="Academic",
            source=SearchSource.ARXIV,
            url="https://arxiv.org/1234",
            score=0.7,
        ),
    ]

    crossref_results = [
        make_search_result(
            title="CrossRef Research",
            source=SearchSource.CROSSREF,
            url="https://doi.org/10.1234/example",
            score=0.8,
        ),
    ]

    wikipedia_results = [
        make_search_result(
            title="Artificial Intelligence - Wikipedia",
            source=SearchSource.WIKIPEDIA,
            url="https://en.wikipedia.org/wiki/Artificial_intelligence",
            score=0.6,
        ),
    ]

    result = await merge_documents_node(
        {
            "web_results": web_results,
            "arxiv_results": arxiv_results,
            "crossref_results": crossref_results,
            "wikipedia_results": wikipedia_results,
        }
    )

    assert result["merged_documents"] == [
        web_results[1],
        crossref_results[0],
        arxiv_results[0],
        wikipedia_results[0],
        web_results[0],
    ]


@pytest.mark.asyncio
async def test_merge_documents_node_deduplicates_across_sources():
    web_result = make_search_result(
        title="Web Result",
        source=SearchSource.WEB,
        url="https://example.com/shared",
        score=0.5,
    )

    crossref_result = make_search_result(
        title="CrossRef Duplicate",
        source=SearchSource.CROSSREF,
        url="https://example.com/shared",
        score=0.9,
    )

    wikipedia_result = make_search_result(
        title="Wikipedia Duplicate",
        source=SearchSource.WIKIPEDIA,
        url="https://example.com/shared",
        score=0.8,
    )

    result = await merge_documents_node(
        {
            "web_results": [web_result],
            "arxiv_results": [],
            "crossref_results": [crossref_result],
            "wikipedia_results": [wikipedia_result],
        }
    )

    assert len(result["merged_documents"]) == 1

    # First document with the URL wins.
    assert result["merged_documents"][0] == web_result


@pytest.mark.asyncio
async def test_merge_documents_node_empty():
    result = await merge_documents_node(
        {
            "web_results": [],
            "arxiv_results": [],
            "crossref_results": [],
            "wikipedia_results": [],
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
            source=SearchSource.WEB,
            url=f"https://example.com/{i}",
            score=float(i),
        )
        for i in range(15)
    ]

    result = await merge_documents_node(
        {
            "web_results": documents,
            "arxiv_results": [],
            "crossref_results": [],
            "wikipedia_results": [],
        }
    )

    assert len(result["merged_documents"]) == 10

    assert [document.title for document in result["merged_documents"]] == [
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
            source=SearchSource.WEB,
            url="https://example.com/no-score",
            score=None,
        ),
        make_search_result(
            title="Scored",
            source=SearchSource.WEB,
            url="https://example.com/scored",
            score=0.8,
        ),
        make_search_result(
            title="Wikipedia No Score",
            source=SearchSource.WIKIPEDIA,
            url="https://en.wikipedia.org/wiki/AI",
            score=None,
        ),
    ]

    result = await merge_documents_node(
        {
            "web_results": documents[:2],
            "arxiv_results": [],
            "crossref_results": [],
            "wikipedia_results": [documents[2]],
        }
    )

    assert result["merged_documents"] == [
        documents[1],
        documents[0],
        documents[2],
    ]
