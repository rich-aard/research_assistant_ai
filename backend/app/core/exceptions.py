class ApplicationError(Exception):
    """Base exception for expected application errors."""


class ResearchNotFoundError(ApplicationError):
    """Raised when a research task does not exist."""

    def __init__(self, research_id):
        self.research_id = research_id
        super().__init__(
            f"Research task '{research_id}' was not found."
        )


class ResearchCreationError(ApplicationError):
    """Raised when a research task cannot be created."""


class ResearchPersistenceError(ApplicationError):
    """Raised when a research task cannot be persisted."""