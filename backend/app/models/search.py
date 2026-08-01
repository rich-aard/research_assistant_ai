from datetime import UTC, datetime

from pydantic import BaseModel, Field, HttpUrl

from backend.app.models.enums import SearchSource


class SearchResult(BaseModel):
    """
    A single document retrieved from an external search source.
    """

    title: str = Field(
        description="Title of the retrieved document.",
    )

    url: HttpUrl = Field(
        description="Source URL of the document.",
    )

    content: str = Field(
        description="Extracted content or summary of the document.",
    )

    source: SearchSource = Field(
        description="Source of the document (e.g. tavily, arxiv).",
    )

    score: float | None = Field(
        default=None,
        description="Relevance score assigned by the search provider.",
    )

    snippet: str | None = Field(
        default=None,
        description="Short preview of the document.",
    )

    retrieved_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when the document was retrieved.",
    )
