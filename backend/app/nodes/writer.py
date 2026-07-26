from backend.app.clients.groq import get_llm
from backend.app.core.logging import get_logger
from backend.app.models.search import SearchResult
from backend.app.models.state import ResearchState
from backend.app.prompts.writer_prompt import writer_prompt

logger = get_logger(__name__)

llm = get_llm()

writer_chain = writer_prompt | llm


def _format_documents(results: list[SearchResult], limit: int = 5) -> str:
    """
    Format retrieved documents into a prompt-friendly string.
    """
    if not results:
        return "No results available."

    formatted: list[str] = []

    for result in results[:limit]:
        formatted.append(
            "\n".join(
                [
                    f"Title: {result.title}",
                    f"Source: {result.source}",
                    f"URL: {result.url}",
                    f"Content: {result.content}",
                ]
            )
        )

    return "\n\n".join(formatted)

def _format_sources(results: list[SearchResult], limit: int = 5) -> str:
    """
    Format source references for citation in the report.
    """
    if not results:
        return "No sources available."

    sources: list[str] = []

    for index, result in enumerate(results[:limit], start=1):
        sources.append("\n".join(
        [
            f"[{index}] {result.title}",
            str(result.url),
        ]
        )
    )

    return "\n\n".join(sources)



async def writer_node(state: ResearchState) -> ResearchState:
    """
    Generate the final research report and executive summary
    from the collected web and academic search results.
    """
    topic = state.get("topic")

    if not topic:
        raise ValueError("Research topic is missing.")

    depth = state.get("depth", "standard")
    research_plan = state.get("research_plan", [])

    merged_documents = state.get("merged_documents", [])

    try:
        response = await writer_chain.ainvoke(
            {
                "topic": topic,
                "depth": depth,
                "research_plan": "\n".join(research_plan),
                "documents": _format_documents(merged_documents),
                "sources": _format_sources(merged_documents),
            }
        )

        report = response.content

        logger.info(
            "Generated research report for '%s'",
            topic,
        )

    except Exception as exc:
        logger.exception(
            "Failed to generate report for '%s': %s",
            topic,
            exc,
        )

        report = (
            f"# {topic}\n\n"
            "The research report could not be generated because an unexpected error occurred."
        )

    return {
        **state,
        "report": report,
        "summary": "",
        "status": "writing",
        "progress": 90,
    }
