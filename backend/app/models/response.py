from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ResearchStartResponse(BaseModel):
    """Immediate response to POST /research"""

    research_id: UUID = Field(description="Unique identifier for the research session.")
    status: Literal[
        "queued",
        "processing",
        "completed",
        "failed",
    ] = Field(
        default="queued",
        description="Task status (queued, processing, completed, failed).",
    )
    message: str = Field(description="Human-readable status message.")

    progress: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Current progress percentage.",
    )


class ResearchResultResponse(BaseModel):
    """Current state of a research task."""

    research_id: UUID = Field(description="Unique identifier for the research session.")
    topic: str = Field(description="Research topic.")
    summary: str = Field(description="Concise summary of the generated report.")
    report: str = Field(description="Full research report in Markdown format.")
    status: Literal[
        "queued",
        "processing",
        "completed",
        "failed",
    ] = Field(description="Final execution status.")
    created_at: datetime = Field(
        description="Timestamp when the research was completed."
    )
