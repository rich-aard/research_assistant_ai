from backend.app.core.logging import get_logger
from backend.app.models.search import SearchResult
from backend.app.models.state import ResearchState

logger = get_logger(__name__)


def _deduplicate_documents(
    documents: list[SearchResult],
) -> list[SearchResult]:
    """
    Remove duplicate documents using their URL as the unique key.
    """
    unique_documents: dict[str, SearchResult] = {}

    for document in documents:
        unique_documents.setdefault(
            str(document.url),
            document,
        )

    return list(unique_documents.values())


async def merge_documents_node(
    state: ResearchState,
) -> ResearchState:
    """
    Merge, deduplicate, and rank retrieved documents before
    passing them to the writer.
    """
    web_results = state.get("web_results", [])
    arxiv_results = state.get("arxiv_results", [])
    crossref_results = state.get("crossref_results", [])
    wikipedia_results = state.get("wikipedia_results", [])

    documents = [
        *web_results,
        *arxiv_results,
        *crossref_results,
        *wikipedia_results,
    ]

    documents = _deduplicate_documents(documents)

    documents.sort(
        key=lambda document: document.score or 0.0,
        reverse=True,
    )

    logger.info(
        "Merged %d document(s) into %d unique document(s)",
        len(web_results)
        + len(arxiv_results)
        + len(crossref_results)
        + len(wikipedia_results),
        len(documents),
    )

    return {
        "merged_documents": documents[:10],
    }
