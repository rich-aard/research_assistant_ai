import time
from typing import Any

import requests

from frontend.api.research import (
    get_research,
    start_research,
    stream_research,
)


def start_new_research(
    topic: str,
    depth: int,
) -> dict[str, Any]:
    """
    Start a new research job.

    This is a thin wrapper around the research API client and
    returns the initial research state.
    """
    return start_research(
        topic=topic,
        depth=depth,
    )


def run_research(
    research_id: str,
    timeout_seconds: int = 300,
) -> dict[str, Any]:
    """
    Monitor a research job until completion or failure.

    Args:
        research_id: ID returned by ``start_new_research``.
        timeout_seconds: Maximum allowed execution time.

    Returns:
        A dictionary containing the current research state.
    """
    state: dict[str, Any] = {
        "research_id": research_id,
        "status": "running",
        "stage": None,
        "progress": 0,
        "message": None,
        "summary": None,
        "report": None,
        "sources": [],
        "error": None,
    }

    started_at = time.monotonic()

    try:
        for event in stream_research(research_id):
            elapsed = time.monotonic() - started_at

            if elapsed >= timeout_seconds:
                state["status"] = "timeout"
                state["error"] = (
                    f"Research did not complete within {timeout_seconds} seconds."
                )
                break

            event_type = event["event"]
            data = event.get("data", {})

            if not isinstance(data, dict):
                data = {"raw": data}

            if event_type == "progress" or event_type == "stage":
                _update_progress_state(
                    state,
                    data,
                )

            elif event_type == "complete":
                _complete_research(
                    state,
                    research_id,
                )
                break

            elif event_type == "error":
                _fail_research(
                    state,
                    data,
                )
                break

        else:
            # SSE stream ended without a terminal event.
            if state["status"] == "running":
                _resolve_closed_stream(
                    state,
                    research_id,
                )

    except requests.RequestException as exc:
        _fail_research(
            state,
            {
                "message": f"Network error: {exc}",
            },
        )

    except (ValueError, KeyError, TypeError) as exc:
        _fail_research(
            state,
            {
                "message": f"Unexpected error: {exc}",
            },
        )

    return state


def _update_progress_state(
    state: dict[str, Any],
    data: dict[str, Any],
) -> None:
    """Update local state from a progress/stage event."""
    if "progress" in data:
        state["progress"] = data["progress"]

    if "stage" in data:
        state["stage"] = data["stage"]

    if "message" in data:
        state["message"] = data["message"]


def _complete_research(
    state: dict[str, Any],
    research_id: str,
) -> None:
    """Fetch and store the final research result."""
    result = get_research(research_id)

    state.update(result)
    state["status"] = "completed"
    state["error"] = None


def _fail_research(
    state: dict[str, Any],
    data: dict[str, Any],
) -> None:
    """Mark the local research state as failed."""
    state["status"] = "failed"

    message = data.get("message")

    if message:
        state["error"] = str(message)
    elif data.get("raw"):
        state["error"] = str(data["raw"])
    else:
        state["error"] = "Research failed."


def _resolve_closed_stream(
    state: dict[str, Any],
    research_id: str,
) -> None:
    """
    Resolve a stream that closed without a terminal event.

    The backend may close the connection after completion, so perform
    one final status request before declaring the workflow failed.
    """
    try:
        result = get_research(research_id)

    except requests.RequestException as exc:
        _fail_research(
            state,
            {
                "message": (
                    "Research stream ended and the final "
                    f"status could not be retrieved: {exc}"
                ),
            },
        )
        return

    state.update(result)

    if result["status"] == "completed":
        state["status"] = "completed"
        state["error"] = None
        return

    if result["status"] == "failed":
        state["status"] = "failed"
        state["error"] = result.get(
            "error",
            "Research failed.",
        )
        return

    state["status"] = "failed"
    state["error"] = "Research stream ended before completion."
