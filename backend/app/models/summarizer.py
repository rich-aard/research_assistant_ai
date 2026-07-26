from pydantic import BaseModel, Field


class SummarizerOutput(BaseModel):
    """
    Structured output from the summarizer LLM.
    """

    summary: str = Field(
        description=(
            "A concise executive summary of the research report in 2–3 sentences."
        )
    )
