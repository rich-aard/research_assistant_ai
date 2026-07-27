from datetime import datetime
from uuid import UUID

from typing_extensions import TypedDict

from backend.app.models.enums import ResearchDepth
from backend.app.models.search import SearchResult


class ResearchState(TypedDict, total=False):
    """
    Shared state passed between LangGraph nodes.
    """

    # Metadata
    research_id: UUID
    topic: str
    depth: ResearchDepth
    created_at: datetime

    # Planning
    research_plan: list[str]

    # Search Queries
    web_queries: list[str]
    arxiv_queries: list[str]

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
