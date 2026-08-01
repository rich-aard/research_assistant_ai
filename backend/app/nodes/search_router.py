from collections import defaultdict

from langgraph.types import Send

from backend.app.core.logging import get_logger
from backend.app.models.enums import SearchSource
from backend.app.models.search_query import SearchQuery
from backend.app.models.state import ResearchState

logger = get_logger(__name__)

# Maps logical search sources to LangGraph node names.
SOURCE_NODES = {
    SearchSource.WEB: "web_search",
    SearchSource.ARXIV: "arxiv_search",
    SearchSource.CROSSREF: "crossref_search",
    SearchSource.WIKIPEDIA: "wikipedia_search",
}


def search_router_node(
    state: ResearchState,
) -> list[Send]:
    """
    Fan out search queries to source-specific search nodes.
    """

    search_queries = state.get("search_queries", [])

    if not search_queries:
        logger.warning(
            "search_router received no search_queries",
        )
        return []

    grouped: dict[
        SearchSource,
        list[SearchQuery],
    ] = defaultdict(list)

    for search_query in search_queries:
        if not isinstance(search_query, SearchQuery):
            logger.warning(
                "Skipping invalid search query: %r",
                search_query,
            )
            continue

        for source in search_query.sources:
            if source not in SOURCE_NODES:
                logger.warning(
                    "Unknown search source %r for query %r",
                    source,
                    search_query.query,
                )
                continue

            grouped[source].append(search_query)

    sends = [
        Send(
            SOURCE_NODES[source],
            {
                "queries": queries,
            },
        )
        for source, queries in grouped.items()
    ]

    if not sends:
        logger.warning(
            "search_router found no recognized sources among %d queries",
            len(search_queries),
        )

    return sends
