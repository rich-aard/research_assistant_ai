from functools import lru_cache

from tavily import TavilyClient

from backend.app.core.config import settings
from backend.app.core.logging import get_logger
from backend.app.models.search import SearchResult

logger = get_logger(__name__)


@lru_cache
def get_tavily_client() -> TavilyClient:
    """
    Return a cached Tavily client instance.
    """
    return TavilyClient(api_key=settings.tavily_api_key)


def search_web(
    query: str,
    *,
    max_results: int = 5,
) -> list[SearchResult]:
    """
    Search the web using Tavily and return normalized search results.
    """
    logger.info(
        "Searching Tavily for '%s'",
        query,
    )

    client = get_tavily_client()

    try:
        response = client.search(
            query=query,
            max_results=max_results,
            include_answer=False,
            include_images=False,
        )
    except Exception:
        logger.exception(
            "Tavily search failed for '%s'",
            query,
        )
        raise

    results: list[SearchResult] = []

    for item in response.get("results", []):
        results.append(
            SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                content=item.get("content", ""),
                source="tavily",
                score=item.get("score"),
                snippet=item.get("content"),
            )
        )

    logger.info(
        "Retrieved %d Tavily result(s) for '%s'",
        len(results),
        query,
    )

    return results