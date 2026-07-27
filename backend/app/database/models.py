import uuid
from datetime import UTC, datetime

from sqlalchemy import Enum as SAEnum
from sqlalchemy import Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime

from backend.app.database.base import Base
from backend.app.models.enums import ResearchDepth, TaskStatus


class ResearchTaskORM(Base):
    __tablename__ = "research_tasks"

    research_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    topic: Mapped[str] = mapped_column(String(250), nullable=False)

    depth: Mapped[ResearchDepth] = mapped_column(
        SAEnum(ResearchDepth, name="research_depth"),
        nullable=False,
        default=ResearchDepth.STANDARD,
    )

    status: Mapped[TaskStatus] = mapped_column(
        SAEnum(TaskStatus, name="task_status"),
        nullable=False,
        default=TaskStatus.QUEUED,
    )

    progress: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    report: Mapped[str | None] = mapped_column(Text, nullable=True)

    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    def __repr__(self) -> str:
        return (
            f"ResearchTaskORM("
            f"research_id={self.research_id}, "
            f"status={self.status}, "
            f"progress={self.progress})"
        )
