from typing import Literal

from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    topic: str = Field(
        ..., min_length=3, max_length=250, description="The topic of research"
    )

    depth: Literal["quick", "standard", "comprehensive"] = "standard"
