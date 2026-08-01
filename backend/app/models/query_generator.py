from pydantic import BaseModel, Field

from backend.app.models.search_query import SearchQuery


class QueryGeneratorOutput(BaseModel):
    """
    Optimized search queries generated from the research plan.
    """

    queries: list[SearchQuery] = Field(
        description=(
            "Optimized search queries and the sources "
            "where each query should be executed."
        ),
    )
