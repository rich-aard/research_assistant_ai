from datetime import UTC, datetime
from uuid import UUID, uuid4

from backend.app.core.logging import get_logger
from backend.app.graph import build_graph
from backend.app.models.request import ResearchRequest
from backend.app.models.state import ResearchState
from backend.app.models.task import ResearchTask
from backend.app.storage.research_store import create_task, get_task, update_task

logger = get_logger(__name__)


class ResearchService:
    def __init__(self) -> None:
        self.graph = build_graph()

    def start_research(self, request: ResearchRequest) -> ResearchTask:
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
            status="queued",
            progress=0,
            created_at=datetime.now(UTC),
        )
        return create_task(task)

    def get_research(self, research_id: UUID) -> ResearchTask | None:
        """Fetch research task status"""
        return get_task(research_id)

    async def execute_research(self, research_id: UUID) -> None:
        """
        Execute the LangGraph workflow for a queued research task.

        The resulting summary, report, status, and completion time
        are persisted to the research store.
        """
        task = get_task(research_id)

        if task is None:
            logger.warning(
                "Research task %s not found",
                research_id,
            )
            return

        # Update to processing
        update_task(research_id, status="processing", progress=0)

        # Build initial state
        state: ResearchState = {
            "research_id": research_id,
            "topic": task.topic,
            "depth": task.depth,
            "status": "processing",
            "progress": 0,
            "created_at": task.created_at,
        }

        try:
            logger.info(
                "Research task %s is processing",
                research_id,
            )

            final_state = await self.graph.ainvoke(state)

            update_task(
                research_id,
                status="completed",
                summary=final_state.get("summary", ""),
                report=final_state.get("report", ""),
                progress=100,
                completed_at=datetime.now(UTC),
            )

            logger.info(
                "Research task %s completed",
                research_id,
            )
        except Exception as exc:
            update_task(
                research_id,
                status="failed",
                error=str(exc),
                completed_at=datetime.now(UTC),
            )
            logger.exception(
                "Research task %s failed",
                research_id,
            )
