from pydantic import BaseModel, Field


class PlannerOutput(BaseModel):
    """Structured output returned by the planner LLM."""

    research_plan: list[str] = Field(
        description="Ordered list of research steps."
    )