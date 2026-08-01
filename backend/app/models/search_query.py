from pydantic import BaseModel, Field

from backend.app.models.enums import SearchSource


class SearchQuery(BaseModel):
    """A search query and the providers that should execute it."""

    query: str = Field(
        description="Optimized search query.",
    )

    sources: list[SearchSource] = Field(
        description="Search providers that should execute this query.",
    )
