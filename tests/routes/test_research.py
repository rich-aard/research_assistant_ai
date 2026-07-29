from datetime import UTC, datetime
from uuid import uuid4

import pytest
from httpx import AsyncClient

from backend.app.models.enums import (
    ResearchDepth,
    TaskStage,
    TaskStatus,
)
from backend.app.models.task import ResearchTask


@pytest.mark.asyncio
async def test_start_research(client: AsyncClient, mocker):
    research_id = uuid4()
    depth = ResearchDepth.QUICK
    mock_task = ResearchTask(
        research_id=research_id,
        topic="Artificial Intelligence",
        depth=depth.value,
        status=TaskStatus.QUEUED,
        stage=TaskStage.QUEUED,
        progress=0,
        created_at=datetime.now(UTC),
    )

    mock_start = mocker.patch(
        "backend.app.api.routes.research.research_service.start_research",
        return_value=mock_task,
    )

    mock_execute = mocker.patch(
        "backend.app.api.routes.research.research_service.execute_research",
    )

    response = await client.post(
        "/research",
        json={
            "topic": "Artificial Intelligence",
            "depth": depth.value,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["research_id"] == str(research_id)
    assert data["status"] == "queued"
    assert data["stage"] == "queued"
    assert data["progress"] == 0
    assert data["message"] == "Research started for 'Artificial Intelligence'."

    mock_start.assert_awaited_once()
    mock_execute.assert_awaited_once_with(research_id)


@pytest.mark.asyncio
async def test_start_research_validation_error(
    client: AsyncClient,
    mocker,
):
    mock_start = mocker.patch(
        "backend.app.api.routes.research.research_service.start_research",
    )

    response = await client.post(
        "/research",
        json={
            "topic": "",
            "depth": "invalid",
        },
    )

    assert response.status_code == 422

    mock_start.assert_not_called()


@pytest.mark.asyncio
async def test_get_research(
    client: AsyncClient,
    mocker,
):
    research_id = uuid4()

    mock_task = ResearchTask(
        research_id=research_id,
        topic="Artificial Intelligence",
        depth=ResearchDepth.QUICK,
        status=TaskStatus.COMPLETED,
        stage=TaskStage.COMPLETED,
        progress=100,
        summary="Short summary",
        report="# Report",
        created_at=datetime.now(UTC),
    )

    mock_get = mocker.patch(
        "backend.app.api.routes.research.research_service.get_research",
        return_value=mock_task,
    )

    response = await client.get(f"/research/{research_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["research_id"] == str(research_id)
    assert data["topic"] == "Artificial Intelligence"
    assert data["status"] == TaskStatus.COMPLETED.value
    assert data["stage"] == TaskStage.COMPLETED.value
    assert data["progress"] == 100
    assert data["summary"] == "Short summary"
    assert data["report"] == "# Report"

    mock_get.assert_awaited_once_with(research_id)


@pytest.mark.asyncio
async def test_get_research_not_found(
    client: AsyncClient,
    mocker,
):
    research_id = uuid4()

    mock_get = mocker.patch(
        "backend.app.api.routes.research.research_service.get_research",
        return_value=None,
    )

    response = await client.get(f"/research/{research_id}")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Research task not found.",
    }

    mock_get.assert_awaited_once_with(research_id)


@pytest.mark.asyncio
async def test_stream_research_not_found(
    client: AsyncClient,
    mocker,
):
    research_id = uuid4()

    mock_get = mocker.patch(
        "backend.app.api.routes.research.research_service.get_research",
        return_value=None,
    )

    response = await client.get(
        f"/research/{research_id}/stream",
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Research task not found.",
    }

    mock_get.assert_awaited_once_with(research_id)
