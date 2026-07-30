from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from backend.app.models.enums import ResearchDepth
from backend.app.nodes.planner import planner_node


@pytest.mark.asyncio
async def test_planner_node_success(mocker):
    plan = [
        "Understand the fundamentals of Artificial Intelligence",
        "Review recent AI research",
        "Compare major AI approaches",
        "Summarize key findings",
    ]

    mock_output = mocker.Mock()
    mock_output.research_plan = plan

    mock_chain = mocker.Mock()
    mock_chain.ainvoke = AsyncMock(return_value=mock_output)

    mocker.patch(
        "backend.app.nodes.planner.planner_chain",
        mock_chain,
    )

    state = {
        "research_id": uuid4(),
        "topic": "Artificial Intelligence",
        "depth": ResearchDepth.STANDARD,
    }

    result = await planner_node(state)

    assert result == {
        "research_plan": plan,
    }

    mock_chain.ainvoke.assert_awaited_once_with(
        {
            "topic": "Artificial Intelligence",
            "depth": ResearchDepth.STANDARD,
        }
    )


@pytest.mark.asyncio
async def test_planner_node_fallback(mocker):
    mock_chain = mocker.Mock()
    mock_chain.ainvoke = AsyncMock(
        side_effect=RuntimeError("LLM failed"),
    )

    mocker.patch(
        "backend.app.nodes.planner.planner_chain",
        mock_chain,
    )

    state = {
        "research_id": uuid4(),
        "topic": "Artificial Intelligence",
        "depth": ResearchDepth.STANDARD,
    }

    result = await planner_node(state)

    assert result == {
        "research_plan": [
            "Understand the fundamentals of 'Artificial Intelligence'",
            "Search reliable web sources about 'Artificial Intelligence'",
            "Review academic literature related to 'Artificial Intelligence'",
            "Summarize the key findings and insights",
        ],
    }

    mock_chain.ainvoke.assert_awaited_once_with(
        {
            "topic": "Artificial Intelligence",
            "depth": ResearchDepth.STANDARD,
        }
    )


@pytest.mark.asyncio
async def test_planner_node_missing_topic():
    state = {
        "research_id": uuid4(),
        "depth": ResearchDepth.STANDARD,
    }

    with pytest.raises(
        ValueError,
        match="Research topic is missing.",
    ):
        await planner_node(state)