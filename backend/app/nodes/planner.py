from backend.app.clients.groq import get_llm
from backend.app.core.logging import get_logger
from backend.app.models.planner import PlannerOutput
from backend.app.models.state import ResearchState
from backend.app.prompts.planner_prompt import planner_prompt

logger = get_logger(__name__)

llm = get_llm()
structured_llm = llm.with_structured_output(PlannerOutput)
planner_chain = planner_prompt | structured_llm


async def planner_node(state: ResearchState) -> ResearchState:

    """
    Generate a structured research plan using the configured LLM.

    If the planner fails, a deterministic fallback plan is returned so the workflow can continue.
    """
  
    topic = state.get("topic")

    if not topic:
        raise ValueError("Research topic is missing.")

    depth = state.get("depth", "standard")

    try:
        output = await planner_chain.ainvoke(
            {
                "topic": topic,
                "depth": depth,
            }
        )

        plan = output.research_plan

        logger.info(
            "Generated %d research steps for '%s'",
            len(plan),
            topic,
        )

    except Exception as exc:
        logger.exception(
            "Failed to generate research plan for '%s': %s",
            topic,
            exc,
        )

        plan = [
            f"Understand the fundamentals of '{topic}'",
            f"Search reliable web sources about '{topic}'",
            f"Review academic literature related to '{topic}'",
            "Summarize the key findings and insights",
        ]

    return {
        "research_plan": plan,
    }
