from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from backend.app.models.enums import ResearchDepth
from backend.app.nodes.summarizer import summarizer_node


@pytest.mark.asyncio
async def test_summarizer_node_success(mocker):
    mock_output = mocker.Mock()
    mock_output.summary = (
        "Artificial intelligence has advanced significantly in recent years. "
        "Modern models demonstrate strong capabilities across multiple domains."
    )

    mock_chain = mocker.Mock()
    mock_chain.ainvoke = AsyncMock(return_value=mock_output)

    mocker.patch(
        "backend.app.nodes.summarizer.summarizer_chain",
        mock_chain,
    )

    report = (
        "Artificial intelligence has advanced significantly in recent years. "
        "Modern machine learning models demonstrate strong capabilities "
        "across multiple domains."
    )

    state = {
        "research_id": uuid4(),
        "topic": "Artificial Intelligence",
        "depth": ResearchDepth.STANDARD,
        "report": report,
    }

    result = await summarizer_node(state)

    assert result == {
        "summary": mock_output.summary,
    }

    mock_chain.ainvoke.assert_awaited_once_with(
        {
            "report": report,
        }
    )


@pytest.mark.asyncio
async def test_summarizer_node_missing_report():
    state = {
        "research_id": uuid4(),
        "topic": "Artificial Intelligence",
        "depth": ResearchDepth.STANDARD,
    }

    with pytest.raises(
        ValueError,
        match="Research report is missing.",
    ):
        await summarizer_node(state)


@pytest.mark.asyncio
async def test_summarizer_node_fallback(mocker):
    mock_chain = mocker.Mock()
    mock_chain.ainvoke = AsyncMock(
        side_effect=RuntimeError("LLM failed"),
    )

    mocker.patch(
        "backend.app.nodes.summarizer.summarizer_chain",
        mock_chain,
    )

    report = "A detailed research report about artificial intelligence."

    state = {
        "research_id": uuid4(),
        "topic": "Artificial Intelligence",
        "depth": ResearchDepth.STANDARD,
        "report": report,
    }

    result = await summarizer_node(state)

    assert result == {
        "summary": (
            "Summary generation failed. "
            "Please refer to the full research report."
        ),
    }

    mock_chain.ainvoke.assert_awaited_once_with(
        {
            "report": report,
        }
    )