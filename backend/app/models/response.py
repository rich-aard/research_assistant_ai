from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from backend.app.models.enums import TaskStage, TaskStatus


class ResearchStartResponse(BaseModel):
    """Immediate response to POST /research"""

    research_id: UUID = Field(
        description="Unique identifier for the research session.",
    )
    status: TaskStatus = Field(
        default=TaskStatus.QUEUED,
        description="Current lifecycle status of the research task.",
    )
    stage: TaskStage = Field(
        default=TaskStage.QUEUED,
        description="Current execution stage of the research task.",
    )

    message: str = Field(
        description="Human-readable status message.",
    )

    progress: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Current progress percentage.",
    )


class ResearchResultResponse(BaseModel):
    """Current state of a research task."""

    research_id: UUID = Field(
        description="Unique identifier for the research session.",
    )
    topic: str = Field(
        description="Research topic.",
    )
    summary: str | None = Field(
        default=None,
        description="Concise summary of the generated report.",
    )
    report: str | None = Field(
        default=None,
        description="Full research report in Markdown format.",
    )
    status: TaskStatus = Field(
        description="Current lifecycle status of the research task.",
    )
    stage: TaskStage = Field(
        description="Current execution stage of the research task.",
    )
    progress: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Current progress percentage.",
    )
    created_at: datetime = Field(
        description="Timestamp when the research task was created."
    )
