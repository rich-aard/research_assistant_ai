from datetime import UTC, datetime
from uuid import uuid4

import pytest

from backend.app.events import publisher
from backend.app.models.enums import (
    ResearchDepth,
    TaskStage,
    TaskStatus,
)
from backend.app.models.request import ResearchRequest
from backend.app.models.task import ResearchTask
from backend.app.services.research_service import ResearchService


@pytest.mark.asyncio
async def test_start_research(mocker):
    service = ResearchService()

    request = ResearchRequest(
        topic="Artificial Intelligence",
        depth=ResearchDepth.STANDARD,
    )

    mock_create = mocker.patch(
        "backend.app.repositories.research_repository.ResearchRepository.create",
        return_value=None,
    )

    task = await service.start_research(request)

    assert isinstance(task, ResearchTask)
    assert task.topic == request.topic
    assert task.depth == request.depth
    assert task.status == TaskStatus.QUEUED
    assert task.stage == TaskStage.QUEUED
    assert task.progress == 0
    assert task.created_at is not None

    mock_create.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_research(mocker):
    service = ResearchService()

    research_id = uuid4()

    task = ResearchTask(
        research_id=research_id,
        topic="Artificial Intelligence",
        depth=ResearchDepth.STANDARD,
        status=TaskStatus.COMPLETED,
        stage=TaskStage.COMPLETED,
        progress=100,
        summary="summary",
        report="report",
        created_at=datetime.now(UTC),
    )

    mocker.patch(
        "backend.app.repositories.research_repository.ResearchRepository.get",
        return_value=task,
    )

    result = await service.get_research(research_id)

    assert result == task


@pytest.mark.asyncio
async def test_get_research_not_found(mocker):
    service = ResearchService()

    research_id = uuid4()

    mocker.patch(
        "backend.app.repositories.research_repository.ResearchRepository.get",
        return_value=None,
    )

    result = await service.get_research(research_id)

    assert result is None


@pytest.mark.asyncio
async def test_execute_research_success(mocker):
    service = ResearchService()

    research_id = uuid4()

    task = ResearchTask(
        research_id=research_id,
        topic="Artificial Intelligence",
        depth=ResearchDepth.STANDARD,
        status=TaskStatus.QUEUED,
        stage=TaskStage.QUEUED,
        progress=0,
        created_at=datetime.now(UTC),
    )

    mock_get = mocker.patch(
        "backend.app.repositories.research_repository.ResearchRepository.get",
        return_value=task,
    )

    mock_update = mocker.patch(
        "backend.app.repositories.research_repository.ResearchRepository.update",
    )

    mock_publish = mocker.patch.object(
        publisher,
        "publish",
    )

    mock_shutdown = mocker.patch.object(
        publisher,
        "shutdown",
    )

    async def fake_astream(*args, **kwargs):
        yield {
            "planner": {
                "plan": "plan",
            }
        }

        yield {
            "writer": {
                "summary": "summary",
                "report": "report",
            }
        }

    mocker.patch.object(
        service.graph,
        "astream",
        side_effect=fake_astream,
    )

    await service.execute_research(research_id)

    mock_get.assert_awaited_once()

    assert mock_update.await_count >= 2

    mock_publish.assert_awaited()

    mock_shutdown.assert_awaited_once_with(research_id)

    completed_call = next(
        call
        for call in mock_update.await_args_list
        if call.kwargs.get("status") == TaskStatus.COMPLETED
    )

    assert completed_call.kwargs["summary"] == "summary"
    assert completed_call.kwargs["report"] == "report"
    assert completed_call.kwargs["progress"] == 100
    assert completed_call.kwargs["stage"] == TaskStage.COMPLETED


@pytest.mark.asyncio
async def test_execute_research_failure(mocker):
    service = ResearchService()

    research_id = uuid4()

    task = ResearchTask(
        research_id=research_id,
        topic="Artificial Intelligence",
        depth=ResearchDepth.STANDARD,
        status=TaskStatus.QUEUED,
        stage=TaskStage.QUEUED,
        progress=0,
        created_at=datetime.now(UTC),
    )

    mock_get = mocker.patch(
        "backend.app.repositories.research_repository.ResearchRepository.get",
        return_value=task,
    )

    mocker.patch(
        "backend.app.repositories.research_repository.ResearchRepository.update",
    )

    mock_mark_failed = mocker.patch(
        "backend.app.repositories.research_repository.ResearchRepository.mark_failed",
    )

    mock_publish = mocker.patch.object(
        publisher,
        "publish",
    )

    mock_shutdown = mocker.patch.object(
        publisher,
        "shutdown",
    )

    async def fake_astream(*args, **kwargs):
        if False:
            yield
        raise RuntimeError("Graph failed")

    mocker.patch.object(
        service.graph,
        "astream",
        side_effect=fake_astream,
    )

    await service.execute_research(research_id)

    mock_get.assert_awaited_once()

    mock_mark_failed.assert_awaited_once_with(
        research_id,
        "Graph failed",
    )

    mock_publish.assert_awaited()

    mock_shutdown.assert_awaited_once_with(research_id)

    # Last published event should be the failure event
    _, event = mock_publish.await_args_list[-1].args

    assert event["event"] == "failed"
    assert event["data"]["status"] == TaskStatus.FAILED
    assert event["data"]["stage"] == TaskStage.FAILED
    assert event["data"]["error"] == "Graph failed"
