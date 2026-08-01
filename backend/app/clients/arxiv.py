from functools import lru_cache

import arxiv
from arxiv import Client, Search, SortCriterion

from backend.app.core.logging import get_logger
from backend.app.models.enums import SearchSource
from backend.app.models.search import SearchResult

logger = get_logger(__name__)


@lru_cache
def get_arxiv_client() -> Client:
    """
    Return a cached arXiv client.
    """
    return Client(
        page_size=5,
        delay_seconds=3.0,
        num_retries=3,
    )


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

        results: list[SearchResult] = []

        for paper in papers:
            results.append(
                SearchResult(
                    title=paper.title,
                    url=paper.entry_id,
                    content=paper.summary,
                    snippet=paper.summary,
                    source=SearchSource.ARXIV,
                )
            )

    except arxiv.HTTPError as exc:
        logger.warning(
            "arXiv request failed for '%s': %s",
            query,
            exc,
        )
        return []

    except Exception:
        logger.exception(
            "arXiv search failed for '%s'",
            query,
        )
        raise

    logger.info(
        "Retrieved %d arXiv paper(s) for '%s'",
        len(results),
        query,
    )

    return results
