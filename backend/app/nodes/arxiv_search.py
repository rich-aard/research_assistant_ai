import asyncio

from backend.app.clients.arxiv import search_arxiv
from backend.app.core.logging import get_logger
from backend.app.models.search import SearchResult
from backend.app.models.state import ResearchState

logger = get_logger(__name__)


async def arxiv_search_node(state: ResearchState) -> ResearchState:
    """
    Search arXiv for academic papers corresponding to each research step.
    """
    queries = state.get("arxiv_queries", [])

    logger.info(
        "Running %d arXiv queries",
        len(queries),
    )

    for query in queries:
        logger.info(
            "Running arXiv query: %s",
            query,
        )

    if not queries:
        logger.warning(
            "No arXiv queries available. Skipping arXiv search.",
        )

        return {
            "arxiv_results": [],
        }

    arxiv_results: list[SearchResult] = []

    for query in queries:
        try:
            results = await asyncio.to_thread(
                search_arxiv,
                query,
                max_results=3,
            )

            arxiv_results.extend(results)

            logger.info(
                "Retrieved %d arXiv paper(s) for '%s'",
                len(results),
                query,
            )

        except Exception:
            logger.exception(
                "arXiv search failed for '%s'",
                query,
            )

    logger.info(
        "Collected %d arXiv document(s)",
        len(arxiv_results),
    )

    return {
        "arxiv_results": arxiv_results,
    }
