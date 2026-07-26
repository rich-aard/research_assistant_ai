from pydantic import BaseModel, Field


class QueryGeneratorOutput(BaseModel):
    """
    Optimized search queries generated from the research plan.
    """

    web_queries: list[str] = Field(
        description="Keyword-focused queries optimized for general web search."
    )

    arxiv_queries: list[str] = Field(
        description="Keyword-focused queries optimized for academic literature search."
    )