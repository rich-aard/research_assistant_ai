import streamlit as st
from requests import RequestException

from frontend.app.api.research import get_research, stream_research

REFRESH_INTERVAL = 1


def render_progress() -> None:
    """Display live research progress and transition to results."""

    research_id = st.session_state.get("research_id")

    if not research_id:
        st.error("No research ID found. Please start a new research.")
        st.session_state.page = "form"
        st.stop()

    # Initialize progress state once.
    if "progress_data" not in st.session_state:
        st.session_state.progress_data = {
            "progress": 0.0,
            "stage": "Starting...",
            "message": "Initialising",
            "status": "running",
            "error": None,
        }

    # Create the SSE iterator only once.
    if "research_events" not in st.session_state:
        st.session_state.research_events = stream_research(research_id)

    st.markdown("### Research in Progress")

    progress_bar = st.progress(0.0)
    stage_placeholder = st.empty()
    message_placeholder = st.empty()

    @st.fragment(run_every=REFRESH_INTERVAL)
    def progress_ui() -> None:
        """Refresh the progress UI and consume one SSE event."""

        data = st.session_state.progress_data

        # Failed — terminal, nothing left to poll.
        if data["status"] == "failed":
            st.error(f"Research failed: {data.get('error', 'Unknown error.')}")
            return

        if data["status"] == "completed":
            if "research_result" not in st.session_state:
                try:
                    st.session_state.research_result = get_research(research_id)
                except (RequestException, ValueError) as exc:
                    st.session_state.progress_data.update(
                        {
                            "status": "failed",
                            "error": f"Could not retrieve final result: {exc}",
                        }
                    )
                    st.rerun()
                    return

            st.success("Research complete!")

            if st.button("View Results", type="primary", key="view_results_btn"):
                st.session_state.page = "results"
                st.rerun()
            return

        # Still running: pull the next SSE event and update state.
        _consume_next_event()

        data = st.session_state.progress_data

        if data["status"] == "failed":
            st.error(f"Research failed: {data.get('error', 'Unknown error.')}")
            return

        if data["status"] == "completed":
            _render_progress_state(
                progress_bar,
                stage_placeholder,
                message_placeholder,
            )
            return

        # Normal in-progress state.
        _render_progress_state(
            progress_bar,
            stage_placeholder,
            message_placeholder,
        )

    progress_ui()


def _consume_next_event() -> None:
    """Consume exactly one SSE event and update progress state."""

    try:
        event = next(st.session_state.research_events)

    except StopIteration:
        _resolve_stream_closed()
        return

    except RequestException as exc:
        st.session_state.progress_data.update(
            {
                "status": "failed",
                "error": (f"Network error during progress streaming: {exc}"),
            }
        )
        return

    except Exception as exc: # noqa: BLE001
        st.session_state.progress_data.update(
            {
                "status": "failed",
                "error": (f"Unexpected error during progress streaming: {exc}"),
            }
        )
        return

    data = event.get("data", {})

    if not isinstance(data, dict):
        data = {"raw": data}

    status = data.get("status")
    if hasattr(status, "value"):
        status = status.value

    # Error event
    if status == "failed" or event.get("event") == "error":
        st.session_state.progress_data.update(
            {
                "status": "failed",
                "error": data.get(
                    "message",
                    "Research failed.",
                ),
            }
        )
        return

    # Completion event
    if status == "completed" or event.get("event") in {"complete", "completed"}:
        st.session_state.progress_data.update(
            {
                "status": "completed",
                "progress": 1.0,
                "stage": "Complete",
                "message": "Research finished.",
                "error": None,
            }
        )
        return

    # next stage
    _update_progress(data)


def _render_progress_state(
    progress_bar,
    stage_placeholder,
    message_placeholder,
) -> None:
    """Render the current progress state."""

    data = st.session_state.progress_data

    progress = float(data.get("progress", 0.0))

    # Backend sends 0-100.
    # Streamlit expects 0.0-1.0.
    if progress > 1:
        progress /= 100

    progress = min(max(progress, 0.0), 1.0)

    progress_bar.progress(progress)

    stage_placeholder.info(f"**Stage:** {data.get('stage', 'Unknown')}")

    message_placeholder.caption(data.get("message") or "Research is running...")


def _update_progress(data: dict) -> None:
    """Update progress state from an SSE event."""

    progress = data.get("progress")

    if progress is not None:
        progress = float(progress)

        if progress > 1:
            progress /= 100

        st.session_state.progress_data["progress"] = progress

    if "stage" in data:
        st.session_state.progress_data["stage"] = data["stage"]

    if "message" in data:
        st.session_state.progress_data["message"] = data["message"]

    if "status" in data:
        status = data["status"]

        # Handle Enum values from the backend.
        if hasattr(status, "value"):
            status = status.value

        # Backend processing -> frontend running.
        if status == "processing":
            status = "running"

        st.session_state.progress_data["status"] = status


def _resolve_stream_closed() -> None:
    """
    Reconcile the research state when the SSE stream closes.

    A closed SSE connection does not necessarily mean failure.
    Check the backend one final time.
    """

    research_id = st.session_state.get("research_id")

    if not research_id:
        st.session_state.progress_data.update(
            {
                "status": "failed",
                "error": "Research stream ended unexpectedly.",
            }
        )
        return

    try:
        result = get_research(research_id)

    except RequestException as exc:
        st.session_state.progress_data.update(
            {
                "status": "failed",
                "error": (
                    "Research stream ended and the final "
                    f"status could not be retrieved: {exc}"
                ),
            }
        )
        return

    except ValueError as exc:
        st.session_state.progress_data.update(
            {
                "status": "failed",
                "error": f"Invalid response from server: {exc}",
            }
        )
        return

    status = result.get("status")

    if hasattr(status, "value"):
        status = status.value

    # Backend completed while the SSE connection closed.
    if status == "completed":
        st.session_state.progress_data.update(
            {
                "status": "completed",
                "progress": 1.0,
                "stage": "Complete",
                "message": "Research finished.",
                "error": None,
            }
        )
        return

    # Backend explicitly failed.
    if status == "failed":
        st.session_state.progress_data.update(
            {
                "status": "failed",
                "error": result.get(
                    "error",
                    "Research failed.",
                ),
            }
        )
        return

    # Backend is still running, but the connection disappeared.
    st.session_state.progress_data.update(
        {
            "status": "failed",
            "error": "Research stream ended unexpectedly.",
        }
    )
