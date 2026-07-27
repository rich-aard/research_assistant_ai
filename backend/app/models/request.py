from pydantic import BaseModel, Field

from backend.app.models.enums import ResearchDepth


class ResearchRequest(BaseModel):
    topic: str = Field(
        ..., min_length=3, max_length=250, description="The topic of research"
    )

    depth: ResearchDepth = Field(
        default=ResearchDepth.STANDARD,
        description="Desired depth of the research.",
    )
