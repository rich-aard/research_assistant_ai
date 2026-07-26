from backend.app.models.state import ResearchState


async def planner_node(state: ResearchState) -> ResearchState:
    """
    Generate a simple research plan based on the requested depth.
    """

    topic = state.get("topic", "")
    depth = state.get("depth", "standard")

    if depth == "quick":
        plan = [
            f"Understand '{topic}'",
            "Collect reliable information",
        ]

    elif depth == "standard":
        plan = [
            f"Define '{topic}'",
            "Review academic literature",
            "Gather reliable web resources",
            "Summarize key findings",
        ]

    else:  # comprehensive
        plan = [
            f"Define '{topic}'",
            "Review academic literature",
            "Analyze recent developments",
            "Compare different perspectives",
            "Identify trends and challenges",
            "Generate a comprehensive report",
        ]

    return {
        **state,
        "research_plan": plan,
        "status": "planning",
        "progress": 10,
    }
