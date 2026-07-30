import uuid
from datetime import UTC, datetime

from backend.app.database.models import ResearchTaskORM
from backend.app.models.enums import ResearchDepth, TaskStage, TaskStatus


def test_research_task_orm_defaults():
    task = ResearchTaskORM()

    assert task.research_id is None
    assert task.topic is None
    assert task.depth is None
    assert task.status is None
    assert task.stage is None
    assert task.progress is None
    assert task.summary is None
    assert task.report is None
    assert task.error is None
    assert task.created_at is None
    assert task.completed_at is None


def test_research_task_orm_explicit_values():
    research_id = uuid.uuid4()
    created_at = datetime.now(UTC)

    task = ResearchTaskORM(
        research_id=research_id,
        topic="Artificial Intelligence",
        depth=ResearchDepth.STANDARD,
        status=TaskStatus.QUEUED,
        stage=TaskStage.QUEUED,
        progress=0,
        summary="Research summary",
        report="Research report",
        error=None,
        created_at=created_at,
    )

    assert task.research_id == research_id
    assert task.topic == "Artificial Intelligence"
    assert task.depth == ResearchDepth.STANDARD
    assert task.status == TaskStatus.QUEUED
    assert task.stage == TaskStage.QUEUED
    assert task.progress == 0
    assert task.summary == "Research summary"
    assert task.report == "Research report"
    assert task.error is None
    assert task.created_at == created_at
    assert task.completed_at is None


def test_research_task_orm_nullable_fields():
    task = ResearchTaskORM(
        topic="LLM",
        summary=None,
        report=None,
        error=None,
        completed_at=None,
    )

    assert task.summary is None
    assert task.report is None
    assert task.error is None
    assert task.completed_at is None


def test_research_task_orm_tablename():
    assert ResearchTaskORM.__tablename__ == "research_tasks"


def test_research_task_orm_repr():
    research_id = uuid.uuid4()

    task = ResearchTaskORM(
        research_id=research_id,
        status=TaskStatus.PROCESSING,
        stage=TaskStage.PLANNING,
        progress=25,
    )

    result = repr(task)

    assert "ResearchTaskORM(" in result
    assert f"research_id={research_id}" in result
    assert f"status={TaskStatus.PROCESSING}" in result
    assert f"stage={TaskStage.PLANNING}" in result
    assert "progress=25" in result


def test_research_task_orm_column_configuration():
    table = ResearchTaskORM.__table__

    assert table.name == "research_tasks"

    assert table.c.research_id.primary_key is True
    assert table.c.topic.nullable is False
    assert table.c.depth.nullable is False
    assert table.c.status.nullable is False
    assert table.c.stage.nullable is False
    assert table.c.progress.nullable is False

    assert table.c.summary.nullable is True
    assert table.c.report.nullable is True
    assert table.c.error.nullable is True
    assert table.c.completed_at.nullable is True
    assert table.c.created_at.nullable is False
