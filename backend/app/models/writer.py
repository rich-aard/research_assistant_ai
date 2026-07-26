from pydantic import BaseModel, Field


class WriterOutput(BaseModel):
    """
    Structured output produced by the writer LLM.
    """

    report: str = Field(
        description="Complete research report written in Markdown format."
    )

    summary: str = Field(
        description=(
            "Executive summary of the report in 2–3 concise sentences."
        )
    )