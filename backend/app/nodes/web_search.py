import asyncio

from backend.app.clients.tavily import search_web
from backend.app.core.logging import get_logger
from backend.app.models.search import SearchResult
from backend.app.models.search_query import SearchQuery
from backend.app.models.state import ResearchState

logger = get_logger(__name__)


async def web_search_node(
    state: ResearchState,
) -> ResearchState:
    """
    Search the web for each research step using Tavily.
    """
    queries = state.get("queries", [])

    if not queries:
        logger.warning(
            "No queries available. Skipping web search.",
        )

        return {
            "web_results": [],
        }

    async def _search_one(
        search_query: SearchQuery,
    ) -> list[SearchResult]:
        try:
            results = await asyncio.to_thread(
                search_web,
                search_query.query,
            )
            logger.info(
                "Retrieved %d result(s) for '%s'",
                len(results),
                search_query.query,
            )
            return results
        except Exception:
            logger.exception("Web search failed for '%s'", search_query.query)
            return []

    valid_queries = []

    for search_query in queries:
        if not isinstance(search_query, SearchQuery):
            logger.warning(
                "Skipping invalid Web query: %r",
                search_query,
            )
            continue

        valid_queries.append(search_query)

    results_lists = await asyncio.gather(
        *(_search_one(search_query) for search_query in valid_queries)
    )

    web_results = [result for sublist in results_lists for result in sublist]

    logger.info(
        "Collected %d web document(s)",
        len(web_results),
    )

    return {
        "web_results": web_results,
    }
