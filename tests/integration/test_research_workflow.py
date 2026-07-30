from unittest.mock import AsyncMock, Mock

import pytest

from backend.app.graph.research_graph import build_graph
from backend.app.models.planner import PlannerOutput
from backend.app.models.query_generator import QueryGeneratorOutput
from backend.app.models.search import SearchResult
from backend.app.models.summarizer import SummarizerOutput


@pytest.mark.asyncio
async def test_complete_research_workflow(mocker):
    # Planner
    planner_output = PlannerOutput(
        research_plan=[
            "Define artificial intelligence fundamentals",
            "Review modern machine learning approaches",
            "Examine current AI applications",
            "Identify challenges and limitations",
        ]
    )

    planner_invoke = AsyncMock(return_value=planner_output)

    mocker.patch(
        "backend.app.nodes.planner.planner_chain",
        Mock(ainvoke=planner_invoke),
    )

    # Query generator
    query_output = QueryGeneratorOutput(
        web_queries=[
            "artificial intelligence fundamentals modern applications",
            "machine learning approaches current developments",
            "artificial intelligence applications industry",
            "artificial intelligence challenges limitations",
        ],
        arxiv_queries=[
            "artificial intelligence fundamentals machine learning",
            "modern machine learning approaches artificial intelligence",
            "artificial intelligence applications recent advances",
            "artificial intelligence challenges limitations",
        ],
    )

    query_invoke = AsyncMock(return_value=query_output)

    mocker.patch(
        "backend.app.nodes.query_generator.query_generator_chain",
        Mock(ainvoke=query_invoke),
    )

    #  web results
    web_results = [
        SearchResult(
            title="Artificial Intelligence Overview",
            source="tavily",
            url="https://example.com/ai",
            content="Artificial intelligence enables machines to perform tasks.",
            score=0.9,
        ),
        SearchResult(
            title="Machine Learning Applications",
            source="tavily",
            url="https://example.com/ml",
            content="Machine learning is widely used in modern applications.",
            score=0.8,
        ),
    ]

    web_search_mock = mocker.patch(
        "backend.app.nodes.web_search.search_web",
        side_effect=[
            [web_results[0]],
            [web_results[1]],
            [],
            [],
        ],
    )

    #  arXiv results
    arxiv_results = [
        SearchResult(
            title="Recent Advances in Artificial Intelligence",
            source="arxiv",
            url="https://arxiv.org/example",
            content="Recent research explores advances in artificial intelligence.",
            score=0.95,
        ),
        SearchResult(
            title="Machine Learning Research",
            source="arxiv",
            url="https://arxiv.org/ml",
            content="Academic research continues to improve machine learning.",
            score=0.85,
        ),
    ]

    arxiv_search_mock = mocker.patch(
        "backend.app.nodes.arxiv_search.search_arxiv",
        side_effect=[
            [arxiv_results[0]],
            [arxiv_results[1]],
            [],
            [],
        ],
    )

    # Writer
    writer_response = Mock()
    writer_response.content = (
        "# Artificial Intelligence\n\n"
        "## Executive Overview\n\n"
        "Artificial intelligence is a major area of computer science."
    )

    writer_invoke = AsyncMock(return_value=writer_response)

    mocker.patch(
        "backend.app.nodes.writer.writer_chain",
        Mock(ainvoke=writer_invoke),
    )

    # Summarizer
    summarizer_output = SummarizerOutput(
        summary=(
            "Artificial intelligence enables machines to perform "
            "tasks traditionally requiring human intelligence. "
            "Recent research continues to advance its applications "
            "and capabilities."
        )
    )

    summarizer_invoke = AsyncMock(return_value=summarizer_output)

    mocker.patch(
        "backend.app.nodes.summarizer.summarizer_chain",
        Mock(ainvoke=summarizer_invoke),
    )

    #  workflow
    graph = build_graph()

    result = await graph.ainvoke(
        {
            "topic": "Artificial Intelligence",
            "depth": "quick",
        }
    )

    # Verify final state
    assert result["topic"] == "Artificial Intelligence"
    assert result["depth"] == "quick"

    assert result["research_plan"] == planner_output.research_plan

    assert result["web_queries"] == query_output.web_queries
    assert result["arxiv_queries"] == query_output.arxiv_queries

    assert result["web_results"] == web_results
    assert result["arxiv_results"] == arxiv_results

    assert len(result["merged_documents"]) == 4

    assert result["report"] == writer_response.content
    assert result["summary"] == summarizer_output.summary

    # Verify external boundaries were called
    assert web_search_mock.call_count == len(query_output.web_queries)
    assert arxiv_search_mock.call_count == len(query_output.arxiv_queries)

    planner_invoke.assert_awaited_once()
    query_invoke.assert_awaited_once()
    writer_invoke.assert_awaited_once()
    summarizer_invoke.assert_awaited_once()


@pytest.mark.asyncio
async def test_research_workflow_with_planner_failure(mocker):
    # Planner failure
    planner_invoke = AsyncMock(
        side_effect=RuntimeError("LLM unavailable"),
    )

    mocker.patch(
        "backend.app.nodes.planner.planner_chain",
        Mock(ainvoke=planner_invoke),
    )

    # Query generator
    query_output = QueryGeneratorOutput(
        web_queries=[
            "artificial intelligence fundamentals applications",
        ],
        arxiv_queries=[
            "artificial intelligence fundamentals machine learning",
        ],
    )

    query_invoke = AsyncMock(return_value=query_output)

    mocker.patch(
        "backend.app.nodes.query_generator.query_generator_chain",
        Mock(ainvoke=query_invoke),
    )

    # Search results
    web_result = SearchResult(
        title="Artificial Intelligence Overview",
        source="tavily",
        url="https://example.com/ai",
        content="Artificial intelligence enables machines to perform tasks.",
        score=0.9,
    )

    web_search_mock = mocker.patch(
        "backend.app.nodes.web_search.search_web",
        return_value=[web_result],
    )

    arxiv_result = SearchResult(
        title="Artificial Intelligence Research",
        source="arxiv",
        url="https://arxiv.org/example",
        content="Recent research explores artificial intelligence.",
        score=0.95,
    )

    arxiv_search_mock = mocker.patch(
        "backend.app.nodes.arxiv_search.search_arxiv",
        return_value=[arxiv_result],
    )

    # Writer
    writer_response = Mock()
    writer_response.content = (
        "# Artificial Intelligence\n\n"
        "## Executive Overview\n\n"
        "Artificial intelligence is a major area of research."
    )

    writer_invoke = AsyncMock(return_value=writer_response)

    mocker.patch(
        "backend.app.nodes.writer.writer_chain",
        Mock(ainvoke=writer_invoke),
    )

    # Summarizer
    summarizer_output = SummarizerOutput(
        summary=(
            "Artificial intelligence enables machines to perform "
            "tasks traditionally requiring human intelligence."
        )
    )

    summarizer_invoke = AsyncMock(return_value=summarizer_output)

    mocker.patch(
        "backend.app.nodes.summarizer.summarizer_chain",
        Mock(ainvoke=summarizer_invoke),
    )

    # Execute workflow
    graph = build_graph()

    result = await graph.ainvoke(
        {
            "topic": "Artificial Intelligence",
            "depth": "quick",
        }
    )

    # Verify planner fallback
    expected_fallback_plan = [
        "Understand the fundamentals of 'Artificial Intelligence'",
        "Search reliable web sources about 'Artificial Intelligence'",
        "Review academic literature related to 'Artificial Intelligence'",
        "Summarize the key findings and insights",
    ]

    assert result["research_plan"] == expected_fallback_plan

    # Verify workflow continued after planner failure
    assert result["web_queries"] == query_output.web_queries
    assert result["arxiv_queries"] == query_output.arxiv_queries

    assert result["web_results"] == [web_result]
    assert result["arxiv_results"] == [arxiv_result]

    assert len(result["merged_documents"]) == 2

    assert result["report"] == writer_response.content
    assert result["summary"] == summarizer_output.summary

    # Verify calls
    planner_invoke.assert_awaited_once()
    query_invoke.assert_awaited_once()
    writer_invoke.assert_awaited_once()
    summarizer_invoke.assert_awaited_once()

    assert web_search_mock.call_count == 1
    assert arxiv_search_mock.call_count == 1


@pytest.mark.asyncio
async def test_research_workflow_with_search_failure(mocker):
    # Planner
    planner_output = PlannerOutput(
        research_plan=[
            "Define artificial intelligence fundamentals",
            "Review modern machine learning approaches",
        ]
    )

    planner_invoke = AsyncMock(return_value=planner_output)

    mocker.patch(
        "backend.app.nodes.planner.planner_chain",
        Mock(ainvoke=planner_invoke),
    )

    # Query generator
    query_output = QueryGeneratorOutput(
        web_queries=[
            "artificial intelligence fundamentals",
            "modern machine learning approaches",
        ],
        arxiv_queries=[
            "artificial intelligence machine learning",
            "modern machine learning research",
        ],
    )

    query_invoke = AsyncMock(return_value=query_output)

    mocker.patch(
        "backend.app.nodes.query_generator.query_generator_chain",
        Mock(ainvoke=query_invoke),
    )

    # Web search
    # First query fails, second succeeds.
    web_result = SearchResult(
        title="Machine Learning Applications",
        source="tavily",
        url="https://example.com/ml",
        content="Machine learning is widely used in modern applications.",
        score=0.8,
    )

    web_search_mock = mocker.patch(
        "backend.app.nodes.web_search.search_web",
        side_effect=[
            RuntimeError("Tavily unavailable"),
            [web_result],
        ],
    )

    # arXiv search
    # First query fails, second succeeds.
    arxiv_result = SearchResult(
        title="Machine Learning Research",
        source="arxiv",
        url="https://arxiv.org/ml",
        content="Academic research continues to improve machine learning.",
        score=0.85,
    )

    arxiv_search_mock = mocker.patch(
        "backend.app.nodes.arxiv_search.search_arxiv",
        side_effect=[
            RuntimeError("arXiv unavailable"),
            [arxiv_result],
        ],
    )

    # Writer
    writer_response = Mock()
    writer_response.content = (
        "# Artificial Intelligence\n\n"
        "## Executive Overview\n\n"
        "Machine learning is an important component of modern "
        "artificial intelligence."
    )

    writer_invoke = AsyncMock(return_value=writer_response)

    mocker.patch(
        "backend.app.nodes.writer.writer_chain",
        Mock(ainvoke=writer_invoke),
    )

    # Summarizer
    summarizer_output = SummarizerOutput(
        summary=(
            "Machine learning is an important component of modern "
            "artificial intelligence."
        )
    )

    summarizer_invoke = AsyncMock(return_value=summarizer_output)

    mocker.patch(
        "backend.app.nodes.summarizer.summarizer_chain",
        Mock(ainvoke=summarizer_invoke),
    )

    # Execute workflow
    graph = build_graph()

    result = await graph.ainvoke(
        {
            "topic": "Artificial Intelligence",
            "depth": "quick",
        }
    )

    # Verify successful results were retained
    assert result["web_results"] == [web_result]
    assert result["arxiv_results"] == [arxiv_result]

    # Failed searches should not abort the workflow.
    assert len(result["merged_documents"]) == 2

    assert result["report"] == writer_response.content
    assert result["summary"] == summarizer_output.summary

    # Verify every query was attempted
    assert web_search_mock.call_count == 2
    assert arxiv_search_mock.call_count == 2

    planner_invoke.assert_awaited_once()
    query_invoke.assert_awaited_once()
    writer_invoke.assert_awaited_once()
    summarizer_invoke.assert_awaited_once()
