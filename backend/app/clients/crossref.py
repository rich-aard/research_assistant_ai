from functools import lru_cache

import httpx

from backend.app.core.config import settings
from backend.app.core.logging import get_logger
from backend.app.models.enums import SearchSource
from backend.app.models.search import SearchResult

logger = get_logger(__name__)


@lru_cache
def get_crossref_client() -> httpx.Client:
    """
    Return a cached Crossref HTTP client.
    """
    return httpx.Client(
        base_url=settings.crossref_api_url,
        timeout=10.0,
        headers={
            "User-Agent": f"{settings.app_name}/{settings.app_version}",
        },
    )


def search_crossref(
    query: str,
    *,
    max_results: int = 5,
) -> list[SearchResult]:
    """
    Search Crossref and return normalized search results.
    """
    logger.info(
        "Searching Crossref for '%s'",
        query,
    )

    client = get_crossref_client()

    try:
        response = client.get(
            "",
            params={
                "query": query,
                "rows": max_results,
            },
        )

        response.raise_for_status()

        items = response.json()["message"]["items"]

        results: list[SearchResult] = []

        for item in items:
            title = item.get("title", [""])[0]

            url = item.get(
                "URL",
                item.get("resource", {}).get("primary", {}).get("URL", ""),
            )

            results.append(
                SearchResult(
                    title=title,
                    url=url,
                    content="",
                    snippet=title,
                    source=SearchSource.CROSSREF,
                )
            )

    except httpx.HTTPStatusError as exc:
        logger.warning(
            "Crossref request failed for '%s': %s",
            query,
            exc,
        )
        return []

    except httpx.RequestError as exc:
        logger.warning(
            "Crossref request failed for '%s': %s",
            query,
            exc,
        )
        return []

    except Exception:
        logger.exception(
            "Crossref search failed for '%s'",
            query,
        )
        raise

    logger.info(
        "Retrieved %d Crossref result(s) for '%s'",
        len(results),
        query,
    )

    return results
