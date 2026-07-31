import streamlit as st
from requests import RequestException

from frontend.api.research import get_research, stream_research

REFRESH_INTERVAL = 1


def render_progress() -> None:
    """Display live research progress and transition to results."""
    research_id = st.session_state.get("research_id")

    if not research_id:
        st.error("No research ID found. Please start a new research.")
        st.session_state.page = "form"
        return

    if "progress_data" not in st.session_state:
        st.session_state.progress_data = {
            "progress": 0.0,
            "stage": "Starting...",
            "message": "Initializing research...",
            "status": "running",
            "error": None,
        }

    if "research_events" not in st.session_state:
        st.session_state.research_events = stream_research(research_id)

    @st.fragment(run_every=REFRESH_INTERVAL)
    def progress_ui() -> None:
        data = st.session_state.progress_data

        if data["status"] == "failed":
            st.error(
                f"Research failed: {data.get('error', 'Unknown error.')}",
            )
            return

        if data["status"] == "completed":
            _load_final_result(research_id)
            return

        _consume_next_event()

        data = st.session_state.progress_data

        st.markdown("### Research in Progress")

        st.progress(
            min(max(data["progress"], 0.0), 1.0),
        )

        st.info(
            f"**Stage:** {data.get('stage', 'Unknown')}",
        )

        st.caption(
            data.get("message") or "Research is running...",
        )

    progress_ui()


def _consume_next_event() -> None:
    """Consume one SSE event and update the progress state."""
    try:
        event = next(st.session_state.research_events)

    except StopIteration:
        st.session_state.progress_data.update(
            {
                "status": "failed",
                "error": "Research stream ended unexpectedly.",
            },
        )
        return

    event_type = event.get("event", "message")
    data = event.get("data", {})

    if not isinstance(data, dict):
        data = {"raw": data}

    if event_type in {"progress", "stage"}:
        _update_progress(data)

    elif event_type == "complete":
        st.session_state.progress_data.update(
            {
                "status": "completed",
                "progress": 1.0,
                "stage": "Complete",
                "message": "Research finished.",
            },
        )

    elif event_type == "error":
        st.session_state.progress_data.update(
            {
                "status": "failed",
                "error": data.get(
                    "message",
                    "Research failed.",
                ),
            },
        )


def _update_progress(data: dict) -> None:
    """Update progress state from an SSE event."""
    progress = data.get("progress")

    if progress is not None:
        # Backend progress is 0-100.
        # Streamlit progress expects 0.0-1.0.
        if progress > 1:
            progress = progress / 100

        st.session_state.progress_data["progress"] = progress

    if "stage" in data:
        st.session_state.progress_data["stage"] = data["stage"]

    if "message" in data:
        st.session_state.progress_data["message"] = data["message"]


def _load_final_result(research_id: str) -> None:
    """Fetch the completed research result once."""
    if "research_result" in st.session_state:
        st.session_state.page = "results"
        st.rerun()

    try:
        st.session_state.research_result = get_research(
            research_id,
        )
        st.session_state.page = "results"
        st.rerun()

    except RequestException as exc:
        st.session_state.progress_data.update(
            {
                "status": "failed",
                "error": f"Could not retrieve final result: {exc}",
            },
        )

    except ValueError as exc:
        st.session_state.progress_data.update(
            {
                "status": "failed",
                "error": f"Invalid response from server: {exc}",
            },
        )
