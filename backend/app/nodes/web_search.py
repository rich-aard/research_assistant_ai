import asyncio

from backend.app.clients.tavily import search_web
from backend.app.core.logging import get_logger
from backend.app.models.search import SearchResult
from backend.app.models.state import ResearchState

logger = get_logger(__name__)


async def web_search_node(state: ResearchState) -> ResearchState:
    """
    Search the web for each research step using Tavily.
    """
    queries = state.get("web_queries", [])

    if not queries:
        logger.warning(
            "No web queries available. Skipping web search.",
        )

        return {
            "web_results": [],
        }

    async def _search_one(query: str) -> list[SearchResult]:
        try:
            results = await asyncio.to_thread(
                search_web,
                query,
            )
            logger.info(
                "Retrieved %d result(s) for '%s'",
                len(results),
                query,
            )
            return results
        except Exception:
            logger.exception("Web search failed for '%s'", query)
            return []

    results_lists = await asyncio.gather(*(_search_one(q) for q in queries))
    web_results = [result for sublist in results_lists for result in sublist]

    logger.info(
        "Collected %d web document(s)",
        len(web_results),
    )

    return {
        "web_results": web_results,
    }
