from datetime import datetime
from typing import Literal, Any
from uuid import UUID

from typing_extensions import TypedDict


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
    web_results: list[dict[str, Any]]
    arxiv_results: list[dict[str, Any]]

    # Before summarization
    web_documents_raw: list[dict[str, Any]]#raw docs of websearch
    arxiv_documents_raw: list[dict[str, Any]]#raw docs of arxiv
    merged_documents: list[dict[str, Any]]#deduplicatd + ranked

    # Final Output
    summary: str
    report: str

    # Errors
    error: str | None