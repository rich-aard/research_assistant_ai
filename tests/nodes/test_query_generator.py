from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from backend.app.models.enums import ResearchDepth
from backend.app.nodes.query_generator import query_generator_node


@pytest.mark.asyncio
async def test_query_generator_node_success(mocker):
    web_queries = [
        "artificial intelligence machine learning recent advances",
        "AI neural network model development techniques",
    ]

    arxiv_queries = [
        "artificial intelligence machine learning recent advances",
        "neural network architectures AI model development",
    ]

    mock_output = mocker.Mock()
    mock_output.web_queries = web_queries
    mock_output.arxiv_queries = arxiv_queries

    mock_chain = mocker.Mock()
    mock_chain.ainvoke = AsyncMock(return_value=mock_output)

    mocker.patch(
        "backend.app.nodes.query_generator.query_generator_chain",
        mock_chain,
    )

    research_plan = [
        "Review recent advances in artificial intelligence",
        "Examine modern neural network architectures",
    ]

    state = {
        "research_id": uuid4(),
        "topic": "Artificial Intelligence",
        "depth": ResearchDepth.STANDARD,
        "research_plan": research_plan,
    }

    result = await query_generator_node(state)

    assert result == {
        "web_queries": web_queries,
        "arxiv_queries": arxiv_queries,
    }

    mock_chain.ainvoke.assert_awaited_once_with(
        {
            "topic": "Artificial Intelligence",
            "research_plan": "\n".join(research_plan),
        }
    )


@pytest.mark.asyncio
async def test_query_generator_node_missing_topic():
    state = {
        "research_id": uuid4(),
        "depth": ResearchDepth.STANDARD,
        "research_plan": [
            "Review artificial intelligence",
        ],
    }

    with pytest.raises(
        ValueError,
        match="Research topic is missing.",
    ):
        await query_generator_node(state)


@pytest.mark.asyncio
async def test_query_generator_node_empty_research_plan(mocker):
    mock_chain = mocker.Mock()
    mock_chain.ainvoke = AsyncMock()

    mocker.patch(
        "backend.app.nodes.query_generator.query_generator_chain",
        mock_chain,
    )

    state = {
        "research_id": uuid4(),
        "topic": "Artificial Intelligence",
        "depth": ResearchDepth.STANDARD,
        "research_plan": [],
    }

    result = await query_generator_node(state)

    assert result == {
        "web_queries": [],
        "arxiv_queries": [],
    }

    mock_chain.ainvoke.assert_not_awaited()


@pytest.mark.asyncio
async def test_query_generator_node_fallback(mocker):
    mock_chain = mocker.Mock()
    mock_chain.ainvoke = AsyncMock(
        side_effect=RuntimeError("LLM failed"),
    )

    mocker.patch(
        "backend.app.nodes.query_generator.query_generator_chain",
        mock_chain,
    )

    research_plan = [
        "Review recent artificial intelligence research",
        "Examine neural network architectures",
        "Study machine learning applications",
    ]

    state = {
        "research_id": uuid4(),
        "topic": "Artificial Intelligence",
        "depth": ResearchDepth.STANDARD,
        "research_plan": research_plan,
    }

    result = await query_generator_node(state)

    assert result == {
        "web_queries": research_plan,
        "arxiv_queries": research_plan,
    }

    mock_chain.ainvoke.assert_awaited_once_with(
        {
            "topic": "Artificial Intelligence",
            "research_plan": "\n".join(research_plan),
        }
    )