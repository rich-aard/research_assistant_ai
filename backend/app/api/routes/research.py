from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, HTTPException

from backend.app.models.request import ResearchRequest
from backend.app.models.response import (
    ResearchResultResponse,
    ResearchStartResponse,
)
from backend.app.services import ResearchService

router = APIRouter(
    prefix="/research",
    tags=["Research"],
)

research_service = ResearchService()


@router.post(
    "",
    response_model=ResearchStartResponse,
)
async def start_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks,
) -> ResearchStartResponse:
    task = research_service.start_research(request)

    background_tasks.add_task(
        research_service.execute_research,
        task.research_id,
    )

    return ResearchStartResponse(
        research_id=task.research_id,
        status=task.status,
        progress=task.progress,
        message=f"Research started for '{task.topic}'.",
    )


@router.get(
    "/{research_id}",
    response_model=ResearchResultResponse,
)
async def get_research(research_id: UUID) -> ResearchResultResponse:
    task = research_service.get_research(research_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Research task not found.",
        )

    return task
