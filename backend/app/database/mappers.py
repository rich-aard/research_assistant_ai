from backend.app.database.models import ResearchTaskORM
from backend.app.models.search import SearchResult
from backend.app.models.task import ResearchTask


def orm_to_model(task: ResearchTaskORM) -> ResearchTask:
    """Convert a SQLAlchemy ORM object into a Pydantic ResearchTask."""
    return ResearchTask(
        research_id=task.research_id,
        topic=task.topic,
        depth=task.depth,
        status=task.status,
        stage=task.stage,
        progress=task.progress,
        summary=task.summary,
        report=task.report,
        sources=[SearchResult.model_validate(source) for source in task.sources],
        error=task.error,
        created_at=task.created_at,
        completed_at=task.completed_at,
    )


def model_to_orm(task: ResearchTask) -> ResearchTaskORM:
    """Convert a Pydantic ResearchTask into a SQLAlchemy ORM object."""
    return ResearchTaskORM(
        research_id=task.research_id,
        topic=task.topic,
        depth=task.depth,
        status=task.status,
        stage=task.stage,
        progress=task.progress,
        summary=task.summary,
        report=task.report,
        sources=[source.model_dump(mode="json") for source in task.sources],
        error=task.error,
        created_at=task.created_at,
        completed_at=task.completed_at,
    )
