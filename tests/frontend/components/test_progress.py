import requests

from frontend.components.progress import (
    _consume_next_event,
    _load_final_result,
    _update_progress,
    render_progress,
)


def test_render_progress_without_research_id(
    mocker,
    session_state,
):
    mocker.patch(
        "frontend.components.progress.st.session_state",
        session_state,
    )

    error = mocker.patch(
        "frontend.components.progress.st.error",
    )

    render_progress()

    error.assert_called_once_with(
        "No research ID found. Please start a new research.",
    )

    assert session_state["page"] == "form"


def test_render_progress_initializes_state(
    mocker,
    session_state,
):
    session_state["research_id"] = "abc123"

    mocker.patch(
        "frontend.components.progress.st.session_state",
        session_state,
    )

    start_stream = mocker.patch(
        "frontend.components.progress.stream_research",
        return_value=iter([]),
    )

    mock_consume = mocker.patch(
        "frontend.components.progress._consume_next_event",
    )

    mocker.patch(
        "frontend.components.progress.st.fragment",
        side_effect=lambda **kwargs: lambda func: func,
    )

    mocker.patch(
        "frontend.components.progress.st.markdown",
    )
    mocker.patch(
        "frontend.components.progress.st.progress",
    )
    mocker.patch(
        "frontend.components.progress.st.info",
    )
    mocker.patch(
        "frontend.components.progress.st.caption",
    )

    render_progress()

    assert session_state["progress_data"] == {
        "progress": 0.0,
        "stage": "Starting...",
        "message": "Initializing research...",
        "status": "running",
        "error": None,
    }

    assert "research_events" in session_state

    start_stream.assert_called_once_with("abc123")
    mock_consume.assert_called_once()


def test_render_progress_does_not_recreate_stream(
    mocker,
    session_state,
):
    existing_stream = iter([])

    session_state.update(
        {
            "research_id": "abc123",
            "progress_data": {
                "progress": 0.5,
                "stage": "searching",
                "message": "Searching...",
                "status": "running",
                "error": None,
            },
            "research_events": existing_stream,
        }
    )

    mocker.patch(
        "frontend.components.progress.st.session_state",
        session_state,
    )

    start_stream = mocker.patch(
        "frontend.components.progress.stream_research",
    )

    mocker.patch(
        "frontend.components.progress.st.fragment",
        side_effect=lambda **kwargs: lambda func: func,
    )

    mocker.patch(
        "frontend.components.progress.st.markdown",
    )
    mocker.patch(
        "frontend.components.progress.st.progress",
    )
    mocker.patch(
        "frontend.components.progress.st.info",
    )
    mocker.patch(
        "frontend.components.progress.st.caption",
    )

    render_progress()

    start_stream.assert_not_called()


def test_consume_progress_event(
    mocker,
    session_state,
):
    session_state["progress_data"] = {
        "progress": 0.0,
        "stage": "Starting...",
        "message": "Initializing research...",
        "status": "running",
        "error": None,
    }

    session_state["research_events"] = iter(
        [
            {
                "event": "progress",
                "data": {
                    "progress": 50,
                    "stage": "web_search",
                    "message": "Searching web...",
                },
            },
        ]
    )

    mocker.patch(
        "frontend.components.progress.st.session_state",
        session_state,
    )

    _consume_next_event()

    assert session_state["progress_data"] == {
        "progress": 0.5,
        "stage": "web_search",
        "message": "Searching web...",
        "status": "running",
        "error": None,
    }


def test_consume_stage_event(
    mocker,
    session_state,
):
    session_state["progress_data"] = {
        "progress": 0.2,
        "stage": "gathering",
        "message": "Gathering sources...",
        "status": "running",
        "error": None,
    }

    session_state["research_events"] = iter(
        [
            {
                "event": "stage",
                "data": {
                    "progress": 75,
                    "stage": "analyzing",
                },
            },
        ]
    )

    mocker.patch(
        "frontend.components.progress.st.session_state",
        session_state,
    )

    _consume_next_event()

    assert session_state["progress_data"]["progress"] == 0.75
    assert session_state["progress_data"]["stage"] == "analyzing"


def test_consume_complete_event(
    mocker,
    session_state,
):
    session_state["progress_data"] = {
        "progress": 0.8,
        "stage": "writing",
        "message": "Writing report...",
        "status": "running",
        "error": None,
    }

    session_state["research_events"] = iter(
        [
            {
                "event": "complete",
                "data": {},
            },
        ]
    )

    mocker.patch(
        "frontend.components.progress.st.session_state",
        session_state,
    )

    _consume_next_event()

    assert session_state["progress_data"] == {
        "progress": 1.0,
        "stage": "Complete",
        "message": "Research finished.",
        "status": "completed",
        "error": None,
    }


def test_consume_error_event(
    mocker,
    session_state,
):
    session_state["progress_data"] = {
        "progress": 0.5,
        "stage": "searching",
        "message": "Searching...",
        "status": "running",
        "error": None,
    }

    session_state["research_events"] = iter(
        [
            {
                "event": "error",
                "data": {
                    "message": "Research failed",
                },
            },
        ]
    )

    mocker.patch(
        "frontend.components.progress.st.session_state",
        session_state,
    )

    _consume_next_event()

    assert session_state["progress_data"]["status"] == "failed"
    assert session_state["progress_data"]["error"] == "Research failed"


def test_consume_error_event_without_message(
    mocker,
    session_state,
):
    session_state["progress_data"] = {
        "progress": 0.5,
        "stage": "searching",
        "message": "Searching...",
        "status": "running",
        "error": None,
    }

    session_state["research_events"] = iter(
        [
            {
                "event": "error",
                "data": {},
            },
        ]
    )

    mocker.patch(
        "frontend.components.progress.st.session_state",
        session_state,
    )

    _consume_next_event()

    assert session_state["progress_data"]["status"] == "failed"
    assert session_state["progress_data"]["error"] == "Research failed."


def test_consume_stream_end(
    mocker,
    session_state,
):
    session_state["progress_data"] = {
        "progress": 0.8,
        "stage": "writing",
        "message": "Writing...",
        "status": "running",
        "error": None,
    }

    session_state["research_events"] = iter([])

    mocker.patch(
        "frontend.components.progress.st.session_state",
        session_state,
    )

    _consume_next_event()

    assert session_state["progress_data"]["status"] == "failed"
    assert (
        session_state["progress_data"]["error"] == "Research stream ended unexpectedly."
    )


def test_consume_non_dict_event_data(
    mocker,
    session_state,
):
    session_state["progress_data"] = {
        "progress": 0.0,
        "stage": "Starting...",
        "message": "Initializing...",
        "status": "running",
        "error": None,
    }

    session_state["research_events"] = iter(
        [
            {
                "event": "progress",
                "data": "invalid payload",
            },
        ]
    )

    mocker.patch(
        "frontend.components.progress.st.session_state",
        session_state,
    )

    _consume_next_event()

    assert session_state["progress_data"]["progress"] == 0.0
    assert session_state["progress_data"]["stage"] == "Starting..."
    assert session_state["progress_data"]["message"] == "Initializing..."


def test_update_progress_converts_percentage_to_fraction(
    mocker,
    session_state,
):
    session_state["progress_data"] = {
        "progress": 0.0,
        "stage": "Starting...",
        "message": "Initializing...",
        "status": "running",
        "error": None,
    }

    mocker.patch(
        "frontend.components.progress.st.session_state",
        session_state,
    )

    _update_progress(
        {
            "progress": 75,
            "stage": "analyzing",
            "message": "Analyzing research...",
        }
    )

    assert session_state["progress_data"]["progress"] == 0.75
    assert session_state["progress_data"]["stage"] == "analyzing"
    assert session_state["progress_data"]["message"] == "Analyzing research..."


def test_update_progress_keeps_fraction(
    mocker,
    session_state,
):
    session_state["progress_data"] = {
        "progress": 0.0,
        "stage": "Starting...",
        "message": "Initializing...",
        "status": "running",
        "error": None,
    }

    mocker.patch(
        "frontend.components.progress.st.session_state",
        session_state,
    )

    _update_progress(
        {
            "progress": 0.75,
        }
    )

    assert session_state["progress_data"]["progress"] == 0.75


def test_update_progress_partial_data(
    mocker,
    session_state,
):
    session_state["progress_data"] = {
        "progress": 0.25,
        "stage": "searching",
        "message": "Searching...",
        "status": "running",
        "error": None,
    }

    mocker.patch(
        "frontend.components.progress.st.session_state",
        session_state,
    )

    _update_progress(
        {
            "stage": "analyzing",
        }
    )

    assert session_state["progress_data"]["progress"] == 0.25
    assert session_state["progress_data"]["stage"] == "analyzing"
    assert session_state["progress_data"]["message"] == "Searching..."


def test_load_final_result_success(
    mocker,
    session_state,
):
    final_result = {
        "research_id": "abc123",
        "topic": "AI",
        "status": "completed",
        "summary": "Summary",
        "report": "Report",
        "sources": [],
    }

    session_state["progress_data"] = {
        "progress": 1.0,
        "stage": "Complete",
        "message": "Research finished.",
        "status": "completed",
        "error": None,
    }

    mocker.patch(
        "frontend.components.progress.st.session_state",
        session_state,
    )

    get_research = mocker.patch(
        "frontend.components.progress.get_research",
        return_value=final_result,
    )

    rerun = mocker.patch(
        "frontend.components.progress.st.rerun",
        side_effect=RuntimeError("rerun"),
    )

    try:
        _load_final_result("abc123")
    except RuntimeError:
        pass

    get_research.assert_called_once_with("abc123")
    assert session_state["research_result"] == final_result
    assert session_state["page"] == "results"
    rerun.assert_called_once()


def test_load_final_result_existing_result(
    mocker,
    session_state,
):
    existing_result = {
        "research_id": "abc123",
        "status": "completed",
    }

    session_state["research_result"] = existing_result

    mocker.patch(
        "frontend.components.progress.st.session_state",
        session_state,
    )

    get_research = mocker.patch(
        "frontend.components.progress.get_research",
    )

    rerun = mocker.patch(
        "frontend.components.progress.st.rerun",
        side_effect=RuntimeError("rerun"),
    )

    try:
        _load_final_result("abc123")
    except RuntimeError:
        pass

    get_research.assert_not_called()
    assert session_state["page"] == "results"
    rerun.assert_called_once()


def test_load_final_result_request_error(
    mocker,
    session_state,
):
    session_state["progress_data"] = {
        "progress": 1.0,
        "stage": "Complete",
        "message": "Research finished.",
        "status": "completed",
        "error": None,
    }

    mocker.patch(
        "frontend.components.progress.st.session_state",
        session_state,
    )

    mocker.patch(
        "frontend.components.progress.get_research",
        side_effect=requests.RequestException("Connection failed"),
    )

    _load_final_result("abc123")

    assert session_state["progress_data"]["status"] == "failed"
    assert (
        session_state["progress_data"]["error"]
        == "Could not retrieve final result: Connection failed"
    )


def test_load_final_result_invalid_response(
    mocker,
    session_state,
):
    session_state["progress_data"] = {
        "progress": 1.0,
        "stage": "Complete",
        "message": "Research finished.",
        "status": "completed",
        "error": None,
    }

    mocker.patch(
        "frontend.components.progress.st.session_state",
        session_state,
    )

    mocker.patch(
        "frontend.components.progress.get_research",
        side_effect=ValueError("Invalid response"),
    )

    _load_final_result("abc123")

    assert session_state["progress_data"]["status"] == "failed"
    assert (
        session_state["progress_data"]["error"]
        == "Invalid response from server: Invalid response"
    )
