from datetime import UTC, datetime
from uuid import uuid4

from backend.app.database.mappers import (
    model_to_orm,
    orm_to_model,
)
from backend.app.models.enums import (
    ResearchDepth,
    TaskStage,
    TaskStatus,
)
from backend.app.models.task import ResearchTask


def create_task() -> ResearchTask:
    return ResearchTask(
        research_id=uuid4(),
        topic="Artificial Intelligence",
        depth=ResearchDepth.STANDARD,
        status=TaskStatus.PROCESSING,
        stage=TaskStage.SUMMARIZING,
        progress=75,
        summary="summary",
        report="report",
        error=None,
        created_at=datetime.now(UTC),
        completed_at=None,
    )


def test_model_to_orm():
    task = create_task()

    orm = model_to_orm(task)

    assert orm.research_id == task.research_id
    assert orm.topic == task.topic
    assert orm.depth == task.depth
    assert orm.status == task.status
    assert orm.stage == task.stage
    assert orm.progress == task.progress
    assert orm.summary == task.summary
    assert orm.report == task.report
    assert orm.error == task.error
    assert orm.created_at == task.created_at
    assert orm.completed_at == task.completed_at


def test_orm_to_model():
    task = create_task()

    orm = model_to_orm(task)

    model = orm_to_model(orm)

    assert model.research_id == orm.research_id
    assert model.topic == orm.topic
    assert model.depth == orm.depth
    assert model.status == orm.status
    assert model.stage == orm.stage
    assert model.progress == orm.progress
    assert model.summary == orm.summary
    assert model.report == orm.report
    assert model.error == orm.error
    assert model.created_at == orm.created_at
    assert model.completed_at == orm.completed_at


def test_round_trip_conversion():
    original = create_task()

    converted = orm_to_model(
        model_to_orm(original),
    )

    assert converted == original