from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.models import ResearchTaskORM
from backend.app.models.enums import TaskStatus


class ResearchRepository:
    """
    Persistence layer for research tasks. Works exclusively with
    ResearchTaskORM — has no knowledge of Pydantic schemas.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, task: ResearchTaskORM) -> ResearchTaskORM:
        """Persist a new research task."""
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def get(self, research_id: UUID) -> ResearchTaskORM | None:
        """Retrieve a research task by its ID."""
        result = await self.session.execute(
            select(ResearchTaskORM).where(
                ResearchTaskORM.research_id == research_id,
            )
        )
        return result.scalar_one_or_none()

    async def update(self, research_id: UUID, **kwargs) -> ResearchTaskORM | None:
        """Update one or more fields of a research task."""
        task = await self.get(research_id)

        if task is None:
            return None

        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)

        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def mark_failed(
        self,
        research_id: UUID,
        error: str,
    ) -> ResearchTaskORM | None:
        """
        Mark a research task as failed and record the error message.
        """
        return await self.update(
            research_id,
            status=TaskStatus.FAILED,
            error=error,
            completed_at=datetime.now(UTC),
        )

    async def list_all(self) -> list[ResearchTaskORM]:
        """Return all research tasks."""
        result = await self.session.execute(select(ResearchTaskORM))
        return list(result.scalars().all())

    async def delete(self, research_id: UUID) -> bool:
        """Delete a research task by its ID."""
        task = await self.get(research_id)

        if task is None:
            return False

        await self.session.delete(task)
        await self.session.commit()
        return True
