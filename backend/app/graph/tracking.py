from types import MappingProxyType

from backend.app.models.enums import TaskStage

NODE_TO_STAGE = MappingProxyType({
    "planner": TaskStage.PLANNING,
    "query_generator": TaskStage.QUERY_GENERATION,
    "web_search": TaskStage.WEB_SEARCH,
    "arxiv_search": TaskStage.ARXIV_SEARCH,
    "merge_documents": TaskStage.MERGING,
    "writer": TaskStage.WRITING_REPORT,
    "summarizer": TaskStage.SUMMARIZING,
})

NODE_TO_PROGRESS = MappingProxyType({
    "planner": 10,
    "query_generator": 20,
    "web_search": 35,
    "arxiv_search": 50,
    "merge_documents": 65,
    "writer": 85,
    "summarizer": 95,
})