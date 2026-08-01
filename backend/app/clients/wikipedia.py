from functools import lru_cache

import requests

from backend.app.core.config import settings
from backend.app.core.logging import get_logger
from backend.app.models.enums import SearchSource
from backend.app.models.search import SearchResult

logger = get_logger(__name__)


@lru_cache
def get_wikipedia_session() -> requests.Session:
    """
    Return a cached Wikipedia HTTP session.
    """
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": f"{settings.app_name}/{settings.app_version}",
        }
    )
    return session


def search_wikipedia(
    query: str,
    *,
    max_results: int = 5,
) -> list[SearchResult]:
    """
    Search Wikipedia and return normalized search results.
    """
    logger.info(
        "Searching Wikipedia for '%s'",
        query,
    )

    session = get_wikipedia_session()

    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": max_results,
        "format": "json",
        "utf8": 1,
    }

    try:
        response = session.get(
            settings.wikipedia_api_url,
            params=params,
            timeout=10,
        )
        response.raise_for_status()

        data = response.json()

        search_items = data.get("query", {}).get("search", [])

        results: list[SearchResult] = []

        for item in search_items:
            page_id = item.get("pageid")
            title = item.get("title")

            if not page_id or not title:
                continue

            page_url = "https://en.wikipedia.org/wiki/" + title.replace(" ", "_")

            snippet = item.get("snippet", "")

            results.append(
                SearchResult(
                    title=title,
                    url=page_url,
                    content=snippet,
                    snippet=snippet,
                    source=SearchSource.WIKIPEDIA,
                )
            )

    except requests.RequestException as exc:
        logger.warning(
            "Wikipedia request failed for '%s': %s",
            query,
            exc,
        )
        return []

    except Exception:
        logger.exception(
            "Wikipedia search failed for '%s'",
            query,
        )
        raise

    logger.info(
        "Retrieved %d Wikipedia result(s) for '%s'",
        len(results),
        query,
    )

    return results
