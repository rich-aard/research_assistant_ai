import asyncio
import json
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks
from sse_starlette.sse import EventSourceResponse
from starlette.requests import Request

from backend.app.core.logging import get_logger
from backend.app.events import publisher
from backend.app.models.request import ResearchRequest
from backend.app.models.response import (
    ResearchResultResponse,
    ResearchStartResponse,
)
from backend.app.services import ResearchService

logger = get_logger(__name__)
router = APIRouter(
    prefix="/research",
    tags=["Research"],
)

research_service = ResearchService()


def _serialize_event(event: dict) -> dict:
    """
    Ensure an SSE event's `data` field is a JSON string.

    """
    data = event.get("data")

    if isinstance(data, (dict, list)):
        event = {
            **event,
            "data": json.dumps(data, default=str),
        }

    return event


@router.post(
    "",
    response_model=ResearchStartResponse,
    status_code=202,
)
async def start_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks,
) -> ResearchStartResponse:
    task = await research_service.start_research(request)

    background_tasks.add_task(
        research_service.execute_research,
        task.research_id,
    )

    return ResearchStartResponse(
        research_id=task.research_id,
        status=task.status,
        stage=task.stage,
        progress=task.progress,
        message=f"Research started for '{task.topic}'.",
    )


@router.get(
    "/{research_id}",
    response_model=ResearchResultResponse,
)
async def get_research(
    research_id: UUID,
) -> ResearchResultResponse:
    task = await research_service.get_research(research_id)
    return task


@router.get("/{research_id}/stream")
async def stream_research(
    research_id: UUID,
    request: Request,
) -> EventSourceResponse:
    """
    Stream live research progress using Server-Sent Events (SSE).
    """
    logger.debug("SSE client connected for %s", research_id)

    task = await research_service.get_research(research_id)
    queue = publisher.subscribe(research_id)

    async def event_generator():
        try:
            yield _serialize_event(
                {
                    "event": "progress",
                    "data": {
                        "status": task.status,
                        "stage": task.stage,
                        "progress": task.progress,
                    },
                }
            )
            while True:
                if await request.is_disconnected():
                    break

                event = await queue.get()

                if event is None:
                    break
                logger.debug("Sending SSE event %s", event["event"])
                yield _serialize_event(event)

        except asyncio.CancelledError:
            pass

        finally:
            publisher.unsubscribe(research_id, queue)

    return EventSourceResponse(
        event_generator(),
        ping=15,
    )
