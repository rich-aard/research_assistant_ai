from backend.app.clients.groq import get_llm
from backend.app.core.logging import get_logger
from backend.app.models.state import ResearchState
from backend.app.prompts.writer_prompt import writer_prompt

logger = get_logger(__name__)

llm = get_llm()

writer_chain = writer_prompt | llm


def _format_results(results: list, limit: int = 5) -> str:
    """
    Format retrieved search results into a prompt-friendly string.
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

    web_results = state.get("web_results", [])
    arxiv_results = state.get("arxiv_results", [])

    try:
        response = await writer_chain.ainvoke(
            {
                "topic": topic,
                "depth": depth,
                "research_plan": "\n".join(research_plan),
                "web_results": _format_results(web_results),
                "arxiv_results": _format_results(arxiv_results),
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
        "status": "completed",
        "progress": 100,
    }
