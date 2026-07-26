from langchain_core.prompts import ChatPromptTemplate

summarizer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an expert research assistant.

Your task is to produce a concise executive summary of the
provided research report.

Rules:
- Write 2–3 sentences.
- Preserve the main findings.
- Be factual and objective.
- Do not introduce new information.
- Return only the requested structured output.

""",
        ),
        (
            "human",
            """
Research Report:

{report}
""",
        ),
    ]
)
