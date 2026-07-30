from datetime import UTC, datetime
from uuid import uuid4

import pytest

from backend.app.database.mappers import model_to_orm
from backend.app.models.enums import (
    ResearchDepth,
    TaskStage,
    TaskStatus,
)
from backend.app.models.task import ResearchTask
from backend.app.repositories.research_repository import (
    ResearchRepository,
)


@pytest.mark.asyncio
async def test_create(async_session):
    repo = ResearchRepository(async_session)

    task = ResearchTask(
        research_id=uuid4(),
        topic="Artificial Intelligence",
        depth=ResearchDepth.STANDARD,
        status=TaskStatus.QUEUED,
        stage=TaskStage.QUEUED,
        progress=0,
        created_at=datetime.now(UTC),
    )

    orm_task = model_to_orm(task)

    await repo.create(orm_task)

    saved = await repo.get(task.research_id)

    assert saved is not None
    assert saved.topic == task.topic
    assert saved.status == TaskStatus.QUEUED


@pytest.mark.asyncio
async def test_get(async_session):
    repo = ResearchRepository(async_session)

    task = ResearchTask(
        research_id=uuid4(),
        topic="FastAPI",
        depth=ResearchDepth.STANDARD,
        status=TaskStatus.QUEUED,
        stage=TaskStage.QUEUED,
        progress=0,
        created_at=datetime.now(UTC),
    )

    await repo.create(model_to_orm(task))

    result = await repo.get(task.research_id)

    assert result is not None
    assert result.research_id == task.research_id


@pytest.mark.asyncio
async def test_get_not_found(async_session):
    repo = ResearchRepository(async_session)

    result = await repo.get(uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_update(async_session):
    repo = ResearchRepository(async_session)

    task = ResearchTask(
        research_id=uuid4(),
        topic="LLM",
        depth=ResearchDepth.STANDARD,
        status=TaskStatus.QUEUED,
        stage=TaskStage.QUEUED,
        progress=0,
        created_at=datetime.now(UTC),
    )

    await repo.create(model_to_orm(task))

    await repo.update(
        task.research_id,
        status=TaskStatus.PROCESSING,
        stage=TaskStage.PLANNING,
        progress=10,
    )

    updated = await repo.get(task.research_id)

    assert updated.status == TaskStatus.PROCESSING
    assert updated.stage == TaskStage.PLANNING
    assert updated.progress == 10


@pytest.mark.asyncio
async def test_mark_failed(async_session):
    repo = ResearchRepository(async_session)

    task = ResearchTask(
        research_id=uuid4(),
        topic="LLM",
        depth=ResearchDepth.STANDARD,
        status=TaskStatus.QUEUED,
        stage=TaskStage.QUEUED,
        progress=0,
        created_at=datetime.now(UTC),
    )

    await repo.create(model_to_orm(task))

    await repo.mark_failed(
        task.research_id,
        "Graph failed",
    )

    failed = await repo.get(task.research_id)

    assert failed.status == TaskStatus.FAILED
    assert failed.stage == TaskStage.FAILED
    assert failed.error == "Graph failed"


@pytest.mark.asyncio
async def test_update_not_found(async_session):
    repo = ResearchRepository(async_session)

    result = await repo.update(
        uuid4(),
        status=TaskStatus.FAILED,
    )

    assert result is None


@pytest.mark.asyncio
async def test_update_ignores_unknown_field(async_session):
    repo = ResearchRepository(async_session)

    task = ResearchTask(
        research_id=uuid4(),
        topic="LLM",
        depth=ResearchDepth.STANDARD,
        status=TaskStatus.QUEUED,
        stage=TaskStage.QUEUED,
        progress=0,
        created_at=datetime.now(UTC),
    )

    await repo.create(model_to_orm(task))

    updated = await repo.update(
        task.research_id,
        status=TaskStatus.PROCESSING,
        nonexistent_field="ignored",
    )

    assert updated is not None
    assert updated.status == TaskStatus.PROCESSING
    assert not hasattr(updated, "nonexistent_field")


@pytest.mark.asyncio
async def test_list_all(async_session):
    repo = ResearchRepository(async_session)

    tasks = [
        ResearchTask(
            research_id=uuid4(),
            topic="Artificial Intelligence",
            depth=ResearchDepth.STANDARD,
            status=TaskStatus.QUEUED,
            stage=TaskStage.QUEUED,
            progress=0,
            created_at=datetime.now(UTC),
        ),
        ResearchTask(
            research_id=uuid4(),
            topic="Machine Learning",
            depth=ResearchDepth.STANDARD,
            status=TaskStatus.QUEUED,
            stage=TaskStage.QUEUED,
            progress=0,
            created_at=datetime.now(UTC),
        ),
    ]

    for task in tasks:
        await repo.create(model_to_orm(task))

    result = await repo.list_all()

    assert len(result) >= len(tasks)

    result_ids = {task.research_id for task in result}

    for task in tasks:
        assert task.research_id in result_ids


@pytest.mark.asyncio
async def test_delete(async_session):
    repo = ResearchRepository(async_session)

    task = ResearchTask(
        research_id=uuid4(),
        topic="LLM",
        depth=ResearchDepth.STANDARD,
        status=TaskStatus.QUEUED,
        stage=TaskStage.QUEUED,
        progress=0,
        created_at=datetime.now(UTC),
    )

    await repo.create(model_to_orm(task))

    result = await repo.delete(task.research_id)

    assert result is True
    assert await repo.get(task.research_id) is None


@pytest.mark.asyncio
async def test_delete_not_found(async_session):
    repo = ResearchRepository(async_session)

    result = await repo.delete(uuid4())

    assert result is False
