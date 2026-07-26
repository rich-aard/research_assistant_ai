from backend.app.clients.groq import get_llm
from backend.app.core.logging import get_logger
from backend.app.models.state import ResearchState
from backend.app.models.summarizer import SummarizerOutput
from backend.app.prompts.summarizer_prompt import summarizer_prompt

logger = get_logger(__name__)

llm = get_llm()
structured_llm = llm.with_structured_output(
    SummarizerOutput,
)
summarizer_chain = summarizer_prompt | structured_llm


async def summarizer_node(state: ResearchState) -> ResearchState:
    """
    Generate a concise executive summary from the full report.
    """
    topic = state.get("topic", "unknown")

    report = state.get("report")

    if not report:
        raise ValueError("Research report is missing.")

    try:
        output = await summarizer_chain.ainvoke({"report": report})
        summary = output.summary
        logger.info(
            "Generated summary for '%s'.",
            topic,
        )
    except Exception:
        logger.exception(
            "Failed to generate executive summary for '%s'",
            topic,
        )
        summary = "Summary generation failed. Please refer to the full research report."

    return {
        "summary": summary,
        "status": "completed",
        "progress": 100,
    }
