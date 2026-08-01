from backend.app.clients.crossref import search_crossref
from backend.app.core.logging import get_logger
from backend.app.models.search import SearchResult
from backend.app.models.search_query import SearchQuery
from backend.app.models.state import ResearchState

logger = get_logger(__name__)


async def crossref_search_node(
    state: ResearchState,
) -> ResearchState:
    """
    Execute Crossref searches for routed queries.
    """

    queries = state.get("queries", [])

    if not queries:
        logger.warning(
            "No queries available. Skipping Crossref search.",
        )
        return {
            "crossref_results": [],
        }

    results: list[SearchResult] = []

    for search_query in queries:
        if not isinstance(search_query, SearchQuery):
            logger.warning(
                "Skipping invalid Crossref query: %r",
                search_query,
            )
            continue

        try:
            query_results = search_crossref(
                search_query.query,
            )

            results.extend(query_results)

        except Exception:
            logger.exception(
                "Crossref search failed for '%s'",
                search_query.query,
            )

    logger.info(
        "Crossref search completed with %d result(s)",
        len(results),
    )

    return {
        "crossref_results": results,
    }