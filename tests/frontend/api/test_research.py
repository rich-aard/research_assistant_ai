import json
from unittest.mock import MagicMock

import pytest
import requests

from frontend.api.research import (
    get_research,
    start_research,
    stream_research,
)


def test_start_research_success(mocker):
    response = MagicMock()
    response.json.return_value = {
        "research_id": "123",
        "status": "queued",
        "stage": "queued",
        "progress": 0,
        "message": "Research started.",
    }

    mock_post = mocker.patch(
        "frontend.api.research.requests.post",
        return_value=response,
    )

    result = start_research(
        "Artificial Intelligence",
        3,
    )

    mock_post.assert_called_once()

    assert result == {
        "research_id": "123",
        "status": "queued",
        "stage": "queued",
        "progress": 0,
        "message": "Research started.",
    }


def test_start_research_http_error(mocker):
    response = MagicMock()
    response.raise_for_status.side_effect = requests.HTTPError(
        "Bad request",
    )

    mocker.patch(
        "frontend.api.research.requests.post",
        return_value=response,
    )

    with pytest.raises(requests.HTTPError):
        start_research(
            "Artificial Intelligence",
            3,
        )


def test_start_research_malformed_response(mocker):
    response = MagicMock()
    response.json.return_value = {
        "status": "queued",
    }

    mocker.patch(
        "frontend.api.research.requests.post",
        return_value=response,
    )

    with pytest.raises(ValueError, match="research_id"):
        start_research(
            "Artificial Intelligence",
            3,
        )


def test_get_research_success(mocker):
    response = MagicMock()
    response.json.return_value = {
        "research_id": "123",
        "topic": "Artificial Intelligence",
        "status": "completed",
        "stage": "completed",
        "progress": 100,
        "summary": "Research summary.",
        "report": "# Research Report",
        "sources": [],
    }

    mock_get = mocker.patch(
        "frontend.api.research.requests.get",
        return_value=response,
    )

    result = get_research("123")

    mock_get.assert_called_once()

    assert result == {
        "research_id": "123",
        "topic": "Artificial Intelligence",
        "status": "completed",
        "stage": "completed",
        "progress": 100,
        "summary": "Research summary.",
        "report": "# Research Report",
        "sources": [],
    }


def test_get_research_http_error(mocker):
    response = MagicMock()
    response.raise_for_status.side_effect = requests.HTTPError(
        "Not found",
    )

    mocker.patch(
        "frontend.api.research.requests.get",
        return_value=response,
    )

    with pytest.raises(requests.HTTPError):
        get_research("missing-id")


def test_get_research_malformed_response(mocker):
    response = MagicMock()
    response.json.return_value = {
        "topic": "Artificial Intelligence",
    }

    mocker.patch(
        "frontend.api.research.requests.get",
        return_value=response,
    )

    with pytest.raises(ValueError, match="research_id"):
        get_research("123")


def test_stream_research_success(mocker):
    response = MagicMock()

    events = [
        MagicMock(
            event="progress",
            data=json.dumps(
                {
                    "progress": 50,
                    "stage": "web_search",
                },
            ),
        ),
        MagicMock(
            event="complete",
            data=json.dumps(
                {
                    "progress": 100,
                    "status": "completed",
                },
            ),
        ),
    ]

    response.__enter__.return_value = response
    response.__exit__.return_value = None

    client = MagicMock()
    client.events.return_value = iter(events)

    mocker.patch(
        "frontend.api.research.requests.get",
        return_value=response,
    )
    mocker.patch(
        "frontend.api.research.sseclient.SSEClient",
        return_value=client,
    )

    result = list(stream_research("123"))

    assert result == [
        {
            "event": "progress",
            "data": {
                "progress": 50,
                "stage": "web_search",
            },
        },
        {
            "event": "complete",
            "data": {
                "progress": 100,
                "status": "completed",
            },
        },
    ]


def test_stream_research_invalid_json(mocker):
    response = MagicMock()

    event = MagicMock(
        event="message",
        data="not-valid-json",
    )

    response.__enter__.return_value = response
    response.__exit__.return_value = None

    client = MagicMock()
    client.events.return_value = iter([event])

    mocker.patch(
        "frontend.api.research.requests.get",
        return_value=response,
    )
    mocker.patch(
        "frontend.api.research.sseclient.SSEClient",
        return_value=client,
    )

    result = list(stream_research("123"))

    assert result == [
        {
            "event": "message",
            "data": {
                "raw": "not-valid-json",
            },
        },
    ]


def test_stream_research_http_error(mocker):
    response = MagicMock()
    response.raise_for_status.side_effect = requests.HTTPError(
        "Not found",
    )

    response.__enter__.return_value = response
    response.__exit__.return_value = None

    mocker.patch(
        "frontend.api.research.requests.get",
        return_value=response,
    )

    with pytest.raises(requests.HTTPError):
        list(stream_research("missing-id"))
