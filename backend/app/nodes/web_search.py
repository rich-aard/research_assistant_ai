from backend.app.clients.tavily import search_web
from backend.app.core.logging import get_logger
from backend.app.models.search import SearchResult
from backend.app.models.state import ResearchState

logger = get_logger(__name__)


async def web_search_node(state: ResearchState) -> ResearchState:
    """
    Search the web for each research step using Tavily.
    """
    research_plan = state.get("research_plan", [])

    if not research_plan:
        logger.warning("Research plan is empty. Skipping web search.")

        return {
            "web_results": [],
        }

    web_results: list[SearchResult] = []

    for step in research_plan:
        try:
            results = search_web(step)

            web_results.extend(results)

            logger.info(
                "Retrieved %d result(s) for '%s'",
                len(results),
                step,
            )

        except Exception:
            logger.exception(
                "Web search failed for '%s'",
                step,
            )

    logger.info(
        "Collected %d web document(s)",
        len(web_results),
    )

    return {
        "web_results": web_results,
    }
