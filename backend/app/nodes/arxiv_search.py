from backend.app.clients.arxiv import search_arxiv
from backend.app.core.logging import get_logger
from backend.app.models.search import SearchResult
from backend.app.models.state import ResearchState

logger = get_logger(__name__)


async def arxiv_search_node(state: ResearchState) -> ResearchState:
    """
    Search arXiv for academic papers corresponding to each research step.
    """
    research_plan = state.get("research_plan", [])

    if not research_plan:
        logger.warning(
            "Research plan is empty. Skipping arXiv search.",
        )

        return {
            **state,
            "arxiv_results": [],
        }

    arxiv_results: list[SearchResult] = []

    for step in research_plan:
        try:
            results = search_arxiv(
                step,
                max_results=3,
            )

            arxiv_results.extend(results)

            logger.info(
                "Retrieved %d arXiv paper(s) for '%s'",
                len(results),
                step,
            )

        except Exception:
            logger.exception(
                "arXiv search failed for '%s'",
                step,
            )

    logger.info(
        "Collected %d arXiv document(s)",
        len(arxiv_results),
    )

    return {
        **state,
        "arxiv_results": arxiv_results,
        "status": "searching",
        "progress": 60,
    }
