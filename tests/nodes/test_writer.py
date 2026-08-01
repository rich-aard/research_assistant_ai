from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from backend.app.models.enums import ResearchDepth, SearchSource
from backend.app.models.search import SearchResult
from backend.app.nodes.writer import (
    _format_documents,
    _format_sources,
    writer_node,
)


def make_search_result(
    title: str = "AI Research",
    source: SearchSource = SearchSource.WEB,
    url: str = "https://example.com",
    content: str = "Artificial intelligence research content.",
) -> SearchResult:
    return SearchResult(
        title=title,
        source=source,
        url=url,
        content=content,
    )


def test_format_documents():
    results = [
        make_search_result(
            title="AI Research",
            source=SearchSource.WEB,
            url="https://example.com",
            content="Research content",
        ),
        make_search_result(
            title="Machine Learning",
            source=SearchSource.ARXIV,
            url="https://arxiv.org/example",
            content="Academic content",
        ),
    ]

    formatted = _format_documents(results)

    assert "Title: AI Research" in formatted
    assert "Source: web" in formatted
    assert "URL: https://example.com" in formatted
    assert "Content: Research content" in formatted

    assert "Title: Machine Learning" in formatted
    assert "Source: arxiv" in formatted
    assert "URL: https://arxiv.org/example" in formatted
    assert "Content: Academic content" in formatted


def test_format_documents_empty():
    assert _format_documents([]) == "No results available."


def test_format_sources():
    results = [
        make_search_result(
            title="AI Research",
            url="https://example.com",
        ),
        make_search_result(
            title="Machine Learning",
            url="https://arxiv.org/example",
        ),
    ]

    formatted = _format_sources(results)

    assert "[1] AI Research" in formatted
    assert "https://example.com" in formatted

    assert "[2] Machine Learning" in formatted
    assert "https://arxiv.org/example" in formatted


def test_format_sources_empty():
    assert _format_sources([]) == "No sources available."


@pytest.mark.asyncio
async def test_writer_node_success(mocker):
    response = mocker.Mock()
    response.content = "# Artificial Intelligence\n\nResearch report."

    mock_chain = mocker.Mock()
    mock_chain.ainvoke = AsyncMock(return_value=response)

    mocker.patch(
        "backend.app.nodes.writer.writer_chain",
        mock_chain,
    )

    documents = [
        make_search_result(
            title="AI Research",
            source=SearchSource.WEB,
            url="https://example.com",
            content="AI research content.",
        )
    ]

    state = {
        "research_id": uuid4(),
        "topic": "Artificial Intelligence",
        "depth": ResearchDepth.STANDARD,
        "research_plan": [
            "Understand AI fundamentals",
            "Review recent AI research",
        ],
        "merged_documents": documents,
    }

    result = await writer_node(state)

    assert result == {
        "report": "# Artificial Intelligence\n\nResearch report.",
        "summary": "",
    }

    mock_chain.ainvoke.assert_awaited_once()

    call_args = mock_chain.ainvoke.await_args.args[0]

    assert call_args["topic"] == "Artificial Intelligence"
    assert call_args["depth"] == ResearchDepth.STANDARD
    assert "Understand AI fundamentals" in call_args["research_plan"]
    assert "AI Research" in call_args["documents"]
    assert "https://example.com" in call_args["sources"]


@pytest.mark.asyncio
async def test_writer_node_missing_topic():
    state = {
        "research_id": uuid4(),
        "depth": ResearchDepth.STANDARD,
        "research_plan": [],
        "merged_documents": [],
    }

    with pytest.raises(
        ValueError,
        match="Research topic is missing.",
    ):
        await writer_node(state)


@pytest.mark.asyncio
async def test_writer_node_fallback(mocker):
    mock_chain = mocker.Mock()
    mock_chain.ainvoke = AsyncMock(
        side_effect=RuntimeError("LLM failed"),
    )

    mocker.patch(
        "backend.app.nodes.writer.writer_chain",
        mock_chain,
    )

    state = {
        "research_id": uuid4(),
        "topic": "Artificial Intelligence",
        "depth": ResearchDepth.STANDARD,
        "research_plan": [],
        "merged_documents": [],
    }

    result = await writer_node(state)

    assert result == {
        "report": (
            "# Artificial Intelligence\n\n"
            "The research report could not be generated "
            "because an unexpected error occurred."
        ),
        "summary": "",
    }

    mock_chain.ainvoke.assert_awaited_once()
