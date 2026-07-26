from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ResearchTask(BaseModel):
    research_id: UUID

    topic: str

    depth: Literal[
        "quick",
        "standard",
        "comprehensive",
    ]

    status: Literal[
        "queued",
        "processing",
        "completed",
        "failed",
    ]

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