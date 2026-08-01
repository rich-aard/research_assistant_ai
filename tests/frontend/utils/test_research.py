from unittest.mock import patch

import pytest
import requests

from frontend.app.utils import research as research_module


@pytest.fixture
def mock_start_research():
    """Mock the API client used by the utility module."""
    with patch(
        "frontend.app.utils.research.start_research",
    ) as mock:
        yield mock


@pytest.fixture
def mock_get_research():
    """Mock the API client used by the utility module."""
    with patch(
        "frontend.app.utils.research.get_research",
    ) as mock:
        yield mock


@pytest.fixture
def mock_stream_research():
    """Mock the SSE client used by the utility module."""
    with patch(
        "frontend.app.utils.research.stream_research",
    ) as mock:
        yield mock


def test_start_new_research(mock_start_research):
    """start_new_research delegates to the API client."""
    expected = {
        "research_id": "abc123",
        "status": "queued",
        "stage": "queued",
        "progress": 0,
        "message": "Research started.",
    }
    mock_start_research.return_value = expected

    result = research_module.start_new_research(
        topic="Artificial Intelligence",
        depth=3,
    )

    mock_start_research.assert_called_once_with(
        topic="Artificial Intelligence",
        depth=3,
    )
    assert result == expected


def test_run_research_success(
    mock_stream_research,
    mock_get_research,
):
    """A progress sequence followed by complete returns final research."""
    mock_stream_research.return_value = iter(
        [
            {
                "event": "progress",
                "data": {
                    "progress": 20,
                    "stage": "gathering",
                },
            },
            {
                "event": "stage",
                "data": {
                    "progress": 50,
                    "stage": "analyzing",
                },
            },
            {
                "event": "complete",
                "data": {},
            },
        ],
    )

    final_result = {
        "research_id": "abc123",
        "topic": "Artificial Intelligence",
        "status": "completed",
        "stage": "completed",
        "progress": 100,
        "summary": "Summary",
        "report": "# Report",
        "sources": ["source-1"],
    }
    mock_get_research.return_value = final_result

    result = research_module.run_research(
        "abc123",
        timeout_seconds=10,
    )

    assert result["status"] == "completed"
    assert result["progress"] == 100
    assert result["stage"] == "completed"
    assert result["summary"] == "Summary"
    assert result["report"] == "# Report"
    assert result["sources"] == ["source-1"]
    assert result["error"] is None

    mock_get_research.assert_called_once_with("abc123")


def test_run_research_progress_event(mock_stream_research):
    """Progress events update progress, stage, and message."""
    mock_stream_research.return_value = iter(
        [
            {
                "event": "progress",
                "data": {
                    "progress": 50,
                    "stage": "web_search",
                    "message": "Searching web.",
                },
            },
            {
                "event": "error",
                "data": {
                    "message": "Search failed.",
                },
            },
        ],
    )

    result = research_module.run_research(
        "abc123",
        timeout_seconds=10,
    )

    assert result["progress"] == 50
    assert result["stage"] == "web_search"
    assert result["message"] == "Searching web."
    assert result["status"] == "failed"
    assert result["error"] == "Search failed."


def test_run_research_error_event(mock_stream_research):
    """An error SSE event marks the research as failed."""
    mock_stream_research.return_value = iter(
        [
            {
                "event": "error",
                "data": {
                    "message": "Something went wrong.",
                },
            },
        ],
    )

    result = research_module.run_research(
        "abc123",
        timeout_seconds=10,
    )

    assert result["status"] == "failed"
    assert result["error"] == "Something went wrong."


def test_run_research_timeout(mock_stream_research):
    """A research job exceeding the timeout is marked as timed out."""
    mock_stream_research.return_value = iter(
        [
            {
                "event": "progress",
                "data": {
                    "progress": 20,
                    "stage": "gathering",
                },
            },
            {
                "event": "progress",
                "data": {
                    "progress": 50,
                    "stage": "searching",
                },
            },
        ],
    )

    with patch(
        "frontend.app.utils.research.time.monotonic",
        side_effect=[0, 1, 10],
    ):
        result = research_module.run_research(
            "abc123",
            timeout_seconds=5,
        )

    assert result["status"] == "timeout"
    assert result["progress"] == 20
    assert result["stage"] == "gathering"
    assert "5 seconds" in result["error"]


def test_run_research_closed_stream_completed(
    mock_stream_research,
    mock_get_research,
):
    """A closed SSE stream is resolved by checking the final API state."""
    mock_stream_research.return_value = iter(
        [
            {
                "event": "progress",
                "data": {
                    "progress": 80,
                },
            },
        ],
    )

    mock_get_research.return_value = {
        "research_id": "abc123",
        "status": "completed",
        "stage": "completed",
        "progress": 100,
        "summary": "Final summary",
        "report": "Final report",
        "sources": ["source-1"],
    }

    result = research_module.run_research(
        "abc123",
        timeout_seconds=10,
    )

    assert result["status"] == "completed"
    assert result["progress"] == 100
    assert result["summary"] == "Final summary"
    assert result["error"] is None

    mock_get_research.assert_called_once_with("abc123")


def test_run_research_closed_stream_failed(
    mock_stream_research,
    mock_get_research,
):
    """A closed stream followed by failed backend state remains failed."""
    mock_stream_research.return_value = iter(
        [
            {
                "event": "progress",
                "data": {
                    "progress": 40,
                },
            },
        ],
    )

    mock_get_research.return_value = {
        "research_id": "abc123",
        "status": "failed",
        "error": "Backend failure",
    }

    result = research_module.run_research(
        "abc123",
        timeout_seconds=10,
    )

    assert result["status"] == "failed"
    assert result["error"] == "Backend failure"


def test_run_research_closed_stream_incomplete(
    mock_stream_research,
    mock_get_research,
):
    """A closed stream without a terminal backend state fails safely."""
    mock_stream_research.return_value = iter(
        [
            {
                "event": "progress",
                "data": {
                    "progress": 30,
                },
            },
        ],
    )

    mock_get_research.return_value = {
        "research_id": "abc123",
        "status": "running",
        "progress": 30,
    }

    result = research_module.run_research(
        "abc123",
        timeout_seconds=10,
    )

    assert result["status"] == "failed"
    assert result["error"] == ("Research stream ended before completion.")


def test_run_research_network_error(mock_stream_research):
    """Network errors are converted into a failed research state."""
    mock_stream_research.side_effect = requests.RequestException(
        "Connection refused",
    )

    result = research_module.run_research(
        "abc123",
        timeout_seconds=10,
    )

    assert result["status"] == "failed"
    assert result["error"] == ("Network error: Connection refused")


def test_run_research_unexpected_error(mock_stream_research):
    """Unexpected exceptions are converted into a failed state."""
    mock_stream_research.side_effect = ValueError(
        "Unexpected failure",
    )

    result = research_module.run_research(
        "abc123",
        timeout_seconds=10,
    )

    assert result["status"] == "failed"
    assert result["error"] == ("Unexpected error: Unexpected failure")


def test_run_research_final_fetch_network_error(
    mock_stream_research,
    mock_get_research,
):
    """Failure to fetch final state after stream closure is handled."""
    mock_stream_research.return_value = iter(
        [
            {
                "event": "progress",
                "data": {
                    "progress": 50,
                },
            },
        ],
    )

    mock_get_research.side_effect = requests.RequestException(
        "Fetch failed",
    )

    result = research_module.run_research(
        "abc123",
        timeout_seconds=10,
    )

    assert result["status"] == "failed"
    assert "final status could not be retrieved" in result["error"]


def test_update_progress_state():
    """Progress helper updates only fields supplied by the event."""
    state = {
        "progress": 0,
        "stage": None,
        "message": None,
    }

    research_module._update_progress_state(
        state,
        {
            "progress": 75,
            "stage": "writing",
            "message": "Working...",
        },
    )

    assert state["progress"] == 75
    assert state["stage"] == "writing"
    assert state["message"] == "Working..."


def test_fail_research():
    """Failure helper extracts message, raw data, or fallback error."""
    state = {
        "status": "running",
        "error": None,
    }

    research_module._fail_research(
        state,
        {"message": "Failure reason"},
    )

    assert state["status"] == "failed"
    assert state["error"] == "Failure reason"

    state = {
        "status": "running",
        "error": None,
    }

    research_module._fail_research(
        state,
        {"raw": "Raw error"},
    )

    assert state["error"] == "Raw error"

    state = {
        "status": "running",
        "error": None,
    }

    research_module._fail_research(
        state,
        {},
    )

    assert state["error"] == "Research failed."
