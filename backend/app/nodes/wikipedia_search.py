from backend.app.clients.wikipedia import search_wikipedia
from backend.app.core.logging import get_logger
from backend.app.models.search import SearchResult
from backend.app.models.search_query import SearchQuery
from backend.app.models.state import ResearchState

logger = get_logger(__name__)


def wikipedia_search_node(
    state: ResearchState,
) -> dict:
    """
    Execute routed Wikipedia search queries.
    """

    queries = state.get("queries", [])

    if not queries:
        logger.warning(
            "No queries available for Wikipedia search. Skipping."
        )
        return {
            "wikipedia_results": [],
        }

    results: list[SearchResult] = []

    for search_query in queries:
        if not isinstance(search_query, SearchQuery):
            logger.warning(
                "Skipping invalid Wikipedia search query: %r",
                search_query,
            )
            continue

        try:
            query_results = search_wikipedia(
                search_query.query,
            )
            results.extend(query_results)

        except Exception:
            logger.exception(
                "Wikipedia search failed for query '%s'",
                search_query.query,
            )

    logger.info(
        "Wikipedia search completed with %d result(s)",
        len(results),
    )

    return {
        "wikipedia_results": results,
    }