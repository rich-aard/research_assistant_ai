import json
from collections.abc import Iterator
from typing import Any
from urllib.parse import urljoin

import requests
import sseclient

from frontend.utils.config import RESEARCH_ENDPOINT

API_TIMEOUT = 10


def _parse_research_start_response(
    data: dict[str, Any],
) -> dict[str, Any]:
    """Extract fields from a start-research response."""
    if "research_id" not in data:
        raise ValueError("Missing 'research_id' in response.")

    return {
        "research_id": data["research_id"],
        "status": data["status"],
        "stage": data.get("stage"),
        "progress": data.get("progress", 0),
        "message": data.get("message"),
    }


def _parse_research_status_response(
    data: dict[str, Any],
) -> dict[str, Any]:
    """Extract all fields from a status response."""

    if "research_id" not in data:
        raise ValueError("Missing 'research_id' in response.")

    return {
        "research_id": data["research_id"],
        "topic": data["topic"],
        "status": data["status"],
        "stage": data.get("stage"),
        "progress": data.get("progress", 0),
        "summary": data.get("summary"),
        "report": data.get("report"),
        "sources": data.get("sources", []),
    }


def start_research(
    topic: str,
    depth: int,
) -> dict[str, Any]:
    """
    Start a new research job.

    Args:
        topic: The research topic (string).
        depth: Research depth (e.g., 1-5).

    Returns:
        A dict with research_id, status, stage, progress, message.

    Raises:
        requests.HTTPError: If the API returns an error status.
        ValueError: If the response is malformed.
    """

    response = requests.post(
        RESEARCH_ENDPOINT,
        json={
            "topic": topic,
            "depth": depth,
        },
        timeout=API_TIMEOUT,
    )
    response.raise_for_status()

    return _parse_research_start_response(
        response.json(),
    )


def get_research(
    research_id: str,
) -> dict[str, Any]:
    """
    Get the current status and results of a research job.

    Args:
        research_id: The ID returned by start_research().

    Returns:
        A dict with research_id, topic, status, stage, progress,
        summary, report, sources.

    Raises:
        requests.HTTPError: If the API returns an error status.
        ValueError: If the response is malformed.
    """

    response = requests.get(
        urljoin(RESEARCH_ENDPOINT + "/", research_id),
        timeout=API_TIMEOUT,
    )

    response.raise_for_status()

    return _parse_research_status_response(
        response.json(),
    )


def stream_research(
    research_id: str,
) -> Iterator[dict[str, Any]]:
    """
    Stream real‑time progress events for a research job.

    Args:
        research_id: The ID returned by start_research().

    Yields:
        Dictionaries representing SSE events. Each event has at least
        an 'event' field (e.g., 'progress', 'complete', 'error') and
        a 'data' field containing the parsed JSON payload.

    Raises:
        requests.HTTPError: If the initial connection fails.
        sseclient.SSEClientError: If the stream is malformed.
    """
    url = urljoin(
        RESEARCH_ENDPOINT + "/",
        f"{research_id}/stream",
    )

    with requests.get(
        url,
        stream=True,
        timeout=None,
    ) as response:
        response.raise_for_status()

        client = sseclient.SSEClient(response)

        for event in client.events():
            try:
                data = json.loads(event.data)
            except json.JSONDecodeError:
                data = {"raw": event.data}

            yield {
                "event": event.event or "message",
                "data": data,
            }
