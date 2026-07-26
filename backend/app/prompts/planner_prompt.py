from langchain_core.prompts import ChatPromptTemplate

planner_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an expert AI research planner.

Your task is to create a logical research plan for the given topic.

Rules:
- Return between 4 and 8 research steps.
- Each step should be concise and actionable.
- Order the steps logically.
- Do not answer the research topic.
- Focus only on planning.
""",
        ),
        (
            "human",
            """
Topic:
{topic}

Research depth:
{depth}
""",
        ),
    ]
)