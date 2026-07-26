from functools import lru_cache

from arxiv import Client, Search, SortCriterion

from backend.app.core.logging import get_logger
from backend.app.models.search import SearchResult

logger = get_logger(__name__)


@lru_cache
def get_arxiv_client() -> Client:
    """
    Return a cached arXiv client.
    """
    return Client()


def search_arxiv(
    query: str,
    *,
    max_results: int = 5,
) -> list[SearchResult]:
    """
    Search arXiv and return normalized search results.
    """
    logger.info(
        "Searching arXiv for '%s'",
        query,
    )

    client = get_arxiv_client()

    search = Search(
        query=query,
        max_results=max_results,
        sort_by=SortCriterion.Relevance,
    )

    try:
        papers = client.results(search)
    except Exception:
        logger.exception(
            "arXiv search failed for '%s'",
            query,
        )
        raise

    results: list[SearchResult] = []

    for paper in papers:
        results.append(
            SearchResult(
                title=paper.title,
                url=paper.entry_id,
                content=paper.summary,
                snippet=paper.summary,
                source="arxiv",
            )
        )

    logger.info(
        "Retrieved %d arXiv paper(s) for '%s'",
        len(results),
        query,
    )

    return results