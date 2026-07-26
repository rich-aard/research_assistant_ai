from functools import lru_cache

from langchain_groq import ChatGroq

from backend.app.core.config import settings


@lru_cache
def get_llm() -> ChatGroq:
    return ChatGroq(
        model=settings.groq_llm_model,
        api_key=settings.groq_api_key,
        temperature=0,
    )
