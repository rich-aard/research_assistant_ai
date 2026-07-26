from langchain_core.prompts import ChatPromptTemplate

writer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an expert AI research assistant.

Your task is to write a comprehensive research report using ONLY the provided research material.

Requirements:
- Use Markdown.
- Start with a title.
- Write an introduction.
- Organize the report using headings.
- Explain concepts clearly.
- Combine information from both web and academic sources.
- End with a concise conclusion.
- Do not fabricate information.
""",
        ),
        (
            "human",
            """
Topic:
{topic}

Research depth:
{depth}

Research plan:
{research_plan}

Web search results:
{web_results}

Academic papers:
{arxiv_results}
""",
        ),
    ]
)