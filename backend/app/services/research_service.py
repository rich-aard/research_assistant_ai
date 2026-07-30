from datetime import UTC, datetime
from uuid import UUID, uuid4

from backend.app.core.exceptions import ResearchNotFoundError
from backend.app.core.logging import get_logger
from backend.app.database.mappers import model_to_orm, orm_to_model
from backend.app.database.session import async_session_factory
from backend.app.events import publisher
from backend.app.graph import build_graph
from backend.app.graph.tracking import (
    NODE_TO_PROGRESS,
    NODE_TO_STAGE,
)
from backend.app.models.enums import TaskStage, TaskStatus
from backend.app.models.request import ResearchRequest
from backend.app.models.state import ResearchState
from backend.app.models.task import ResearchTask
from backend.app.repositories.research_repository import ResearchRepository

logger = get_logger(__name__)


class ResearchService:
    def __init__(self) -> None:
        self.graph = build_graph()

    async def start_research(self, request: ResearchRequest) -> ResearchTask:
        """Create research task and queue execution"""
        research_id = uuid4()

        logger.info(
            "Starting research task %s",
            research_id,
        )
        task = ResearchTask(
            research_id=research_id,
            topic=request.topic,
            depth=request.depth,
            status=TaskStatus.QUEUED,
            stage=TaskStage.QUEUED,
            progress=0,
            created_at=datetime.now(UTC),
        )
        orm_task = model_to_orm(task)

        async with async_session_factory() as session:
            repo = ResearchRepository(session)
            await repo.create(orm_task)

        return orm_to_model(orm_task)

    async def get_research(
        self,
        research_id: UUID,
    ) -> ResearchTask:
        """Fetch research task status"""
        async with async_session_factory() as session:
            repo = ResearchRepository(session)
            task = await repo.get(research_id)

        if task is None:
            raise ResearchNotFoundError(research_id)

        return orm_to_model(task)

    async def execute_research(self, research_id: UUID) -> None:
        """
        Execute the LangGraph workflow for a queued research task.
        The resulting summary, report, status, and completion time are persisted to the database.
        """
        async with async_session_factory() as session:
            repo = ResearchRepository(session)

            task = await repo.get(research_id)

        if task is None:
            logger.warning(
                "Research task %s not found",
                research_id,
            )
            return

        # Update to processing
        async with async_session_factory() as session:
            repo = ResearchRepository(session)

            await repo.update(
                research_id,
                status=TaskStatus.PROCESSING,
                stage=TaskStage.PLANNING,
                progress=5,
            )

            await publisher.publish(
                research_id,
                {
                    "event": "progress",
                    "data": {
                        "status": TaskStatus.PROCESSING,
                        "stage": TaskStage.PLANNING,
                        "progress": 5,
                    },
                },
            )
        # Build initial state
        state: ResearchState = {
            "research_id": research_id,
            "topic": task.topic,
            "depth": task.depth,
            "created_at": task.created_at,
        }
        try:
            logger.info(
                "Research task %s is processing",
                research_id,
            )
            final_state = state.copy()

            async for event in self.graph.astream(
                state,
                stream_mode="updates",
            ):
                for node_name, node_output in event.items():
                    final_state.update(node_output)

                    if node_name in NODE_TO_STAGE:
                        async with async_session_factory() as session:
                            repo = ResearchRepository(session)

                            await repo.update(
                                research_id,
                                stage=NODE_TO_STAGE[node_name],
                                progress=NODE_TO_PROGRESS[node_name],
                            )

                            await publisher.publish(
                                research_id,
                                {
                                    "event": "progress",
                                    "data": {
                                        "status": TaskStatus.PROCESSING,
                                        "stage": NODE_TO_STAGE[node_name],
                                        "progress": NODE_TO_PROGRESS[node_name],
                                    },
                                },
                            )

            async with async_session_factory() as session:
                repo = ResearchRepository(session)

                await repo.update(
                    research_id,
                    stage=TaskStage.FINALIZING,
                    progress=98,
                )

                await publisher.publish(
                    research_id,
                    {
                        "event": "progress",
                        "data": {
                            "status": TaskStatus.PROCESSING,
                            "stage": TaskStage.FINALIZING,
                            "progress": 98,
                        },
                    },
                )

                await repo.update(
                    research_id,
                    status=TaskStatus.COMPLETED,
                    stage=TaskStage.COMPLETED,
                    summary=final_state.get("summary", ""),
                    report=final_state.get("report", ""),
                    progress=100,
                    completed_at=datetime.now(UTC),
                )

                await publisher.publish(
                    research_id,
                    {
                        "event": "completed",
                        "data": {
                            "status": TaskStatus.COMPLETED,
                            "stage": TaskStage.COMPLETED,
                            "progress": 100,
                            "summary": final_state.get("summary", ""),
                            "report": final_state.get("report", ""),
                        },
                    },
                )
            logger.info(
                "Research task %s completed",
                research_id,
            )
        except Exception as exc:
            async with async_session_factory() as session:
                repo = ResearchRepository(session)
                await repo.mark_failed(
                    research_id,
                    str(exc),
                )

                await publisher.publish(
                    research_id,
                    {
                        "event": "failed",
                        "data": {
                            "status": TaskStatus.FAILED,
                            "stage": TaskStage.FAILED,
                            "error": str(exc),
                        },
                    },
                )
            logger.exception(
                "Research task %s failed.",
                research_id,
              
            )

        finally:
            await publisher.shutdown(research_id)
