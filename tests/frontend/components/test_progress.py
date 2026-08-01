import pytest
from requests import RequestException

from frontend.app.components.progress import (
    _consume_next_event,
    _render_progress_state,
    _resolve_stream_closed,
    _update_progress,
    render_progress,
)

# render_progress


def test_render_progress_without_research_id(
    mocker,
    session_state,
):
    error = mocker.patch(
        "frontend.app.components.progress.st.error",
    )

    stop = mocker.patch(
        "frontend.app.components.progress.st.stop",
        side_effect=RuntimeError("stopped"),
    )

    with pytest.raises(RuntimeError):
        render_progress()

    error.assert_called_once_with("No research ID found. Please start a new research.")
    assert session_state["page"] == "form"
    stop.assert_called_once()


def test_render_progress_initializes_state(
    mocker,
    session_state,
):
    session_state["research_id"] = "abc123"

    mocker.patch(
        "frontend.app.components.progress.stream_research",
        return_value=iter([]),
    )

    mocker.patch(
        "frontend.app.components.progress._consume_next_event",
    )

    mocker.patch(
        "frontend.app.components.progress.st.fragment",
        side_effect=lambda **kwargs: lambda func: func,
    )

    mocker.patch(
        "frontend.app.components.progress.st.markdown",
    )
    mocker.patch(
        "frontend.app.components.progress.st.progress",
    )
    mocker.patch(
        "frontend.app.components.progress.st.empty",
        side_effect=[
            mocker.MagicMock(),
            mocker.MagicMock(),
        ],
    )

    render_progress()

    assert session_state["progress_data"] == {
        "progress": 0.0,
        "stage": "Starting...",
        "message": "Initialising",
        "status": "running",
        "error": None,
    }


def test_render_progress_creates_stream_once(
    mocker,
    session_state,
):
    session_state["research_id"] = "abc123"

    stream = iter([])

    start_stream = mocker.patch(
        "frontend.app.components.progress.stream_research",
        return_value=stream,
    )

    mocker.patch(
        "frontend.app.components.progress._consume_next_event",
    )

    mocker.patch(
        "frontend.app.components.progress.st.fragment",
        side_effect=lambda **kwargs: lambda func: func,
    )

    mocker.patch(
        "frontend.app.components.progress.st.markdown",
    )
    mocker.patch(
        "frontend.app.components.progress.st.progress",
    )
    mocker.patch(
        "frontend.app.components.progress.st.empty",
        side_effect=[
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
        ],
    )

    render_progress()
    render_progress()

    start_stream.assert_called_once_with("abc123")
    assert session_state["research_events"] is stream


# _consume_next_event


def test_consume_progress_event(
    mocker,
    session_state,
):
    session_state["progress_data"] = {
        "progress": 0.0,
        "stage": "Starting...",
        "message": "Initialising",
        "status": "running",
        "error": None,
    }

    session_state["research_events"] = iter(
        [
            {
                "event": "progress",
                "data": {
                    "progress": 35,
                    "stage": "web_search",
                    "message": "Searching the web...",
                },
            }
        ]
    )

    _consume_next_event()

    assert session_state["progress_data"] == {
        "progress": 0.35,
        "stage": "web_search",
        "message": "Searching the web...",
        "status": "running",
        "error": None,
    }


def test_consume_stage_event(
    session_state,
):
    session_state["progress_data"] = {
        "progress": 0.35,
        "stage": "web_search",
        "message": "Searching...",
        "status": "running",
        "error": None,
    }

    session_state["research_events"] = iter(
        [
            {
                "event": "stage",
                "data": {
                    "progress": 50,
                    "stage": "arxiv_search",
                    "message": "Searching arXiv...",
                },
            }
        ]
    )

    _consume_next_event()

    assert session_state["progress_data"] == {
        "progress": 0.5,
        "stage": "arxiv_search",
        "message": "Searching arXiv...",
        "status": "running",
        "error": None,
    }


def test_consume_complete_event(
    session_state,
):
    session_state["progress_data"] = {
        "progress": 0.8,
        "stage": "writing_report",
        "message": "Writing report...",
        "status": "running",
        "error": None,
    }

    session_state["research_events"] = iter(
        [
            {
                "event": "completed",
                "data": {},
            }
        ]
    )

    _consume_next_event()

    assert session_state["progress_data"] == {
        "progress": 1.0,
        "stage": "Complete",
        "message": "Research finished.",
        "status": "completed",
        "error": None,
    }


def test_consume_complete_event_alias(
    session_state,
):
    session_state["progress_data"] = {
        "progress": 0.8,
        "stage": "writing_report",
        "message": "Writing report...",
        "status": "running",
        "error": None,
    }

    session_state["research_events"] = iter(
        [
            {
                "event": "complete",
                "data": {},
            }
        ]
    )

    _consume_next_event()

    assert session_state["progress_data"]["status"] == "completed"
    assert session_state["progress_data"]["progress"] == 1.0


def test_consume_error_event(
    session_state,
):
    session_state["progress_data"] = {
        "progress": 0.5,
        "stage": "web_search",
        "message": "Searching...",
        "status": "running",
        "error": None,
    }

    session_state["research_events"] = iter(
        [
            {
                "event": "error",
                "data": {
                    "message": "Search provider failed.",
                },
            }
        ]
    )

    _consume_next_event()

    assert session_state["progress_data"]["status"] == "failed"
    assert session_state["progress_data"]["error"] == "Search provider failed."


def test_consume_error_event_without_message(
    session_state,
):
    session_state["progress_data"] = {
        "progress": 0.5,
        "stage": "web_search",
        "message": "Searching...",
        "status": "running",
        "error": None,
    }

    session_state["research_events"] = iter(
        [
            {
                "event": "error",
                "data": {},
            }
        ]
    )

    _consume_next_event()

    assert session_state["progress_data"] == {
        "progress": 0.5,
        "stage": "web_search",
        "message": "Searching...",
        "status": "failed",
        "error": "Research failed.",
    }


def test_consume_non_dict_event_data(
    session_state,
):
    session_state["progress_data"] = {
        "progress": 0.2,
        "stage": "web_search",
        "message": "Searching...",
        "status": "running",
        "error": None,
    }

    session_state["research_events"] = iter(
        [
            {
                "event": "progress",
                "data": "invalid data",
            }
        ]
    )

    _consume_next_event()

    # No crash; state remains unchanged because raw data
    # does not contain progress/stage/message fields.
    assert session_state["progress_data"] == {
        "progress": 0.2,
        "stage": "web_search",
        "message": "Searching...",
        "status": "running",
        "error": None,
    }


def test_consume_stream_end(
    mocker,
    session_state,
):
    session_state["research_id"] = "abc123"
    session_state["progress_data"] = {
        "progress": 0.8,
        "stage": "writing_report",
        "message": "Writing...",
        "status": "running",
        "error": None,
    }

    session_state["research_events"] = iter([])

    resolve = mocker.patch(
        "frontend.app.components.progress._resolve_stream_closed",
    )

    _consume_next_event()

    resolve.assert_called_once()


def test_consume_network_error(
    session_state,
):
    session_state["progress_data"] = {
        "progress": 0.5,
        "stage": "web_search",
        "message": "Searching...",
        "status": "running",
        "error": None,
    }

    def failing_iterator():
        raise RequestException("connection lost")
        yield  # pragma: no cover

    session_state["research_events"] = iter(failing_iterator())

    _consume_next_event()

    assert session_state["progress_data"]["status"] == "failed"
    assert (
        "Network error during progress streaming: connection lost"
        in session_state["progress_data"]["error"]
    )


def test_consume_unexpected_error(
    session_state,
):
    session_state["progress_data"] = {
        "progress": 0.5,
        "stage": "web_search",
        "message": "Searching...",
        "status": "running",
        "error": None,
    }

    def failing_iterator():
        raise RuntimeError("unexpected failure")
        yield  # pragma: no cover

    session_state["research_events"] = iter(failing_iterator())

    _consume_next_event()

    assert session_state["progress_data"]["status"] == "failed"
    assert (
        "Unexpected error during progress streaming"
        in session_state["progress_data"]["error"]
    )


# _render_progress_state


def test_render_progress_state_converts_percentage(
    mocker,
    session_state,
):
    session_state["progress_data"] = {
        "progress": 75,
        "stage": "writing_report",
        "message": "Writing...",
        "status": "running",
        "error": None,
    }

    progress_bar = mocker.MagicMock()
    stage_placeholder = mocker.MagicMock()
    message_placeholder = mocker.MagicMock()

    _render_progress_state(
        progress_bar,
        stage_placeholder,
        message_placeholder,
    )

    progress_bar.progress.assert_called_once_with(0.75)
    stage_placeholder.info.assert_called_once_with("**Stage:** writing_report")
    message_placeholder.caption.assert_called_once_with("Writing...")


def test_render_progress_state_keeps_fraction(
    mocker,
    session_state,
):
    session_state["progress_data"] = {
        "progress": 0.65,
        "stage": "merging",
        "message": "Merging documents...",
        "status": "running",
        "error": None,
    }

    progress_bar = mocker.MagicMock()
    stage_placeholder = mocker.MagicMock()
    message_placeholder = mocker.MagicMock()

    _render_progress_state(
        progress_bar,
        stage_placeholder,
        message_placeholder,
    )

    progress_bar.progress.assert_called_once_with(0.65)


def test_render_progress_state_clamps_progress(
    mocker,
    session_state,
):
    session_state["progress_data"] = {
        "progress": 150,
        "stage": "complete",
        "message": "Finished.",
        "status": "completed",
        "error": None,
    }

    progress_bar = mocker.MagicMock()
    stage_placeholder = mocker.MagicMock()
    message_placeholder = mocker.MagicMock()

    _render_progress_state(
        progress_bar,
        stage_placeholder,
        message_placeholder,
    )

    progress_bar.progress.assert_called_once_with(1.0)


def test_render_progress_state_default_message(
    mocker,
    session_state,
):
    session_state["progress_data"] = {
        "progress": 0.2,
        "stage": "processing",
        "message": None,
        "status": "running",
        "error": None,
    }

    progress_bar = mocker.MagicMock()
    stage_placeholder = mocker.MagicMock()
    message_placeholder = mocker.MagicMock()

    _render_progress_state(
        progress_bar,
        stage_placeholder,
        message_placeholder,
    )

    message_placeholder.caption.assert_called_once_with("Research is running...")


# _update_progress


def test_update_progress_converts_percentage(
    session_state,
):
    session_state["progress_data"] = {
        "progress": 0.0,
        "stage": "Starting...",
        "message": "Initialising",
        "status": "running",
        "error": None,
    }

    _update_progress(
        {
            "progress": 80,
            "stage": "writing_report",
            "message": "Writing report...",
        }
    )

    assert session_state["progress_data"]["progress"] == 0.8
    assert session_state["progress_data"]["stage"] == "writing_report"
    assert session_state["progress_data"]["message"] == "Writing report..."


def test_update_progress_keeps_fraction(
    session_state,
):
    session_state["progress_data"] = {
        "progress": 0.0,
        "stage": "Starting...",
        "message": "Initialising",
        "status": "running",
        "error": None,
    }

    _update_progress(
        {
            "progress": 0.45,
        }
    )

    assert session_state["progress_data"]["progress"] == 0.45


def test_update_progress_partial_data(
    session_state,
):
    session_state["progress_data"] = {
        "progress": 0.3,
        "stage": "web_search",
        "message": "Searching...",
        "status": "running",
        "error": None,
    }

    _update_progress(
        {
            "stage": "arxiv_search",
        }
    )

    assert session_state["progress_data"] == {
        "progress": 0.3,
        "stage": "arxiv_search",
        "message": "Searching...",
        "status": "running",
        "error": None,
    }


def test_update_progress_normalizes_processing_status(
    session_state,
):
    session_state["progress_data"] = {
        "progress": 0.3,
        "stage": "web_search",
        "message": "Searching...",
        "status": "running",
        "error": None,
    }

    _update_progress(
        {
            "status": "processing",
        }
    )

    assert session_state["progress_data"]["status"] == "running"


def test_update_progress_accepts_running_status(
    session_state,
):
    session_state["progress_data"] = {
        "progress": 0.3,
        "stage": "web_search",
        "message": "Searching...",
        "status": "running",
        "error": None,
    }

    _update_progress(
        {
            "status": "running",
        }
    )

    assert session_state["progress_data"]["status"] == "running"


# _resolve_stream_closed


def test_resolve_stream_closed_without_research_id(
    mocker,
    session_state,
):
    session_state["progress_data"] = {
        "progress": 0.8,
        "stage": "writing_report",
        "message": "Writing...",
        "status": "running",
        "error": None,
    }

    _resolve_stream_closed()

    assert session_state["progress_data"] == {
        "progress": 0.8,
        "stage": "writing_report",
        "message": "Writing...",
        "status": "failed",
        "error": "Research stream ended unexpectedly.",
    }


def test_resolve_stream_closed_completed(
    mocker,
    session_state,
):
    session_state["research_id"] = "abc123"
    session_state["progress_data"] = {
        "progress": 0.8,
        "stage": "writing_report",
        "message": "Writing...",
        "status": "running",
        "error": None,
    }

    mocker.patch(
        "frontend.app.components.progress.get_research",
        return_value={
            "research_id": "abc123",
            "status": "completed",
        },
    )

    _resolve_stream_closed()

    assert session_state["progress_data"] == {
        "progress": 1.0,
        "stage": "Complete",
        "message": "Research finished.",
        "status": "completed",
        "error": None,
    }


def test_resolve_stream_closed_failed(
    mocker,
    session_state,
):
    session_state["research_id"] = "abc123"
    session_state["progress_data"] = {
        "progress": 0.8,
        "stage": "writing_report",
        "message": "Writing...",
        "status": "running",
        "error": None,
    }

    mocker.patch(
        "frontend.app.components.progress.get_research",
        return_value={
            "research_id": "abc123",
            "status": "failed",
            "error": "Research failed on backend.",
        },
    )

    _resolve_stream_closed()

    assert session_state["progress_data"]["status"] == "failed"
    assert session_state["progress_data"]["error"] == "Research failed on backend."


def test_resolve_stream_closed_active_research(
    mocker,
    session_state,
):
    session_state["research_id"] = "abc123"
    session_state["progress_data"] = {
        "progress": 0.8,
        "stage": "writing_report",
        "message": "Writing...",
        "status": "running",
        "error": None,
    }

    mocker.patch(
        "frontend.app.components.progress.get_research",
        return_value={
            "research_id": "abc123",
            "status": "processing",
        },
    )

    _resolve_stream_closed()

    assert session_state["progress_data"]["status"] == "failed"
    assert (
        session_state["progress_data"]["error"] == "Research stream ended unexpectedly."
    )


def test_resolve_stream_closed_request_error(
    mocker,
    session_state,
):
    session_state["research_id"] = "abc123"
    session_state["progress_data"] = {
        "progress": 0.8,
        "stage": "writing_report",
        "message": "Writing...",
        "status": "running",
        "error": None,
    }

    mocker.patch(
        "frontend.app.components.progress.get_research",
        side_effect=RequestException("connection lost"),
    )

    _resolve_stream_closed()

    assert session_state["progress_data"]["status"] == "failed"
    assert (
        "final status could not be retrieved" in session_state["progress_data"]["error"]
    )


def test_resolve_stream_closed_invalid_response(
    mocker,
    session_state,
):
    session_state["research_id"] = "abc123"
    session_state["progress_data"] = {
        "progress": 0.8,
        "stage": "writing_report",
        "message": "Writing...",
        "status": "running",
        "error": None,
    }

    mocker.patch(
        "frontend.app.components.progress.get_research",
        side_effect=ValueError("Missing research_id"),
    )

    _resolve_stream_closed()

    assert session_state["progress_data"]["status"] == "failed"
    assert (
        session_state["progress_data"]["error"]
        == "Invalid response from server: Missing research_id"
    )