from typing import Any
from uuid import UUID

from backend.app.models.task import ResearchTask

_tasks: dict[UUID, ResearchTask] = {}


def create_task(task: ResearchTask) -> ResearchTask:
    """Store a new research task"""
    _tasks[task.research_id] = task
    return task


def get_task(research_id: UUID) -> ResearchTask | None:
    """Retrieve a research task"""
    return _tasks.get(research_id)


def update_task(research_id: UUID, **kwargs: Any) -> ResearchTask | None:
    """Update an existing research task"""
    task = _tasks.get(research_id)
    if task is None:
        return None

    updated = task.model_copy(update=kwargs)

    _tasks[research_id] = updated

    return updated


def list_tasks() -> list[ResearchTask]:
    """List all research tasks"""
    return list(_tasks.values())


def delete_task(research_id: UUID) -> bool:
    """Delete a research task."""

    return _tasks.pop(research_id, None) is not None
