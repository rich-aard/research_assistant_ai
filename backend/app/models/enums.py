from enum import StrEnum


class TaskStatus(StrEnum):
    """
    Lifecycle status persisted in the database.
    """

    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskStage(StrEnum):
    """
    Fine-grained execution stage.
    Used for progress reporting.
    """

    QUEUED = "queued"
    PLANNING = "planning"
    QUERY_GENERATION = "query_generation"
    WEB_SEARCH = "web_search"
    ARXIV_SEARCH = "arxiv_search"
    MERGING = "merging"
    WRITING_REPORT = "writing_report"
    SUMMARIZING = "summarizing"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    FAILED = "failed"

class ResearchDepth(StrEnum):
    """
    Supported research depth levels.
    """
    QUICK = "quick"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"