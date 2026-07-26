from datetime import datetime
from typing import Literal
from uuid import UUID

from typing_extensions import TypedDict

from backend.app.models.search import SearchResult


class ResearchState(TypedDict, total=False):
    """
    Shared state passed between LangGraph nodes.
    """

    # Metadata
    research_id: UUID
    topic: str
    depth: Literal[
        "quick",
        "standard",
        "comprehensive",
    ]

    created_at: datetime
    completed_at: datetime | None

    # Workflow
    status: Literal[
        "queued",
        "planning",
        "searching",
        "writing",
        "completed",
        "failed",
    ]

    progress: int

    # Planning
    research_plan: list[str]

    # Search Results
    web_results: list[SearchResult]
    arxiv_results: list[SearchResult]

    # Before summarization
    merged_documents: list[SearchResult]

    # Final Output
    summary: str
    report: str

    # Errors
    error: str | None
