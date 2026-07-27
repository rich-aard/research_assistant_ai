from backend.app.clients.groq import get_llm
from backend.app.core.logging import get_logger
from backend.app.models.query_generator import QueryGeneratorOutput
from backend.app.models.state import ResearchState
from backend.app.prompts.query_generator_prompt import query_generator_prompt

logger = get_logger(__name__)

llm = get_llm()
structured_llm = llm.with_structured_output(QueryGeneratorOutput)

query_generator_chain = query_generator_prompt | structured_llm


async def query_generator_node(
    state: ResearchState,
) -> ResearchState:
    """
    Generate optimized search queries for web and academic search.
    """
    topic = state.get("topic")

    if not topic:
        raise ValueError("Research topic is missing.")

    research_plan = state.get("research_plan", [])

    if not research_plan:
        logger.warning(
            "Research plan is empty. Skipping query generation.",
        )

        return {
            "web_queries": [],
            "arxiv_queries": [],
        }

    try:
        output = await query_generator_chain.ainvoke(
            {
                "topic": topic,
                "research_plan": "\n".join(research_plan),
            }
        )

        logger.info(
            "Generated %d web queries and %d arXiv queries for %s",
            len(output.web_queries),
            len(output.arxiv_queries),
            topic,
        )

        return {
            "web_queries": output.web_queries,
            "arxiv_queries": output.arxiv_queries,
        }

    except Exception:
        logger.exception("Failed to generate search queries for '%s'", topic)

        logger.warning(
            "Falling back to research plan as search queries.",
        )

        return {
            "web_queries": research_plan,
            "arxiv_queries": research_plan,
        }
