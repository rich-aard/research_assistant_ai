from datetime import datetime
from uuid import UUID

from typing_extensions import TypedDict

from backend.app.models.enums import ResearchDepth
from backend.app.models.search import SearchResult
from backend.app.models.search_query import SearchQuery


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

    # search queries
    search_queries: list[SearchQuery]

    # routed Search Queries
    queries: list[SearchQuery]

    # Search Results
    crossref_results: list[SearchResult]
    web_results: list[SearchResult]
    arxiv_results: list[SearchResult]
    wikipedia_results: list[SearchResult]

    # Before summarization
    merged_documents: list[SearchResult]

    # Final Output
    summary: str
    report: str

    # Errors
    error: str | None
