from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from backend.app.models.enums import TaskStatus


class ResearchStartResponse(BaseModel):
    """Immediate response to POST /research"""

    research_id: UUID = Field(
        description="Unique identifier for the research session.",
    )
    status: TaskStatus = Field(
        default=TaskStatus.QUEUED,
        description="Current lifecycle status of the research task.",
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
    summary: str = Field(
        description="Concise summary of the generated report.",
    )
    report: str = Field(
        description="Full research report in Markdown format.",
    )
    status: TaskStatus = Field(
        description="Current lifecycle status of the research task.",
    )
    created_at: datetime = Field(
        description="Timestamp when the research task was created."
    )
