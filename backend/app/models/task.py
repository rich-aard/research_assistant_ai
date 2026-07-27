from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from backend.app.models.enums import ResearchDepth, TaskStatus


class ResearchTask(BaseModel):
    """
    In-memory representation of a research task.
    """
    research_id: UUID

    topic: str

    depth: ResearchDepth

    status: TaskStatus=TaskStatus.QUEUED

    progress: int = Field(
        default=0,
        ge=0,
        le=100,
    )

    summary: str | None = None

    report: str | None = None

    error: str | None = None

    created_at: datetime

    completed_at: datetime | None = None
