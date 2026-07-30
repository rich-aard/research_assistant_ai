from uuid import uuid4

from backend.app.core.exceptions import (
    ApplicationError,
    ResearchCreationError,
    ResearchNotFoundError,
    ResearchPersistenceError,
)


def test_application_error():
    error = ApplicationError("Something went wrong")

    assert str(error) == "Something went wrong"


def test_research_not_found_error():
    research_id = uuid4()

    error = ResearchNotFoundError(research_id)

    assert error.research_id == research_id
    assert str(research_id) in str(error)
    assert "not found" in str(error)


def test_research_creation_error():
    error = ResearchCreationError("Could not create research")

    assert str(error) == "Could not create research"


def test_research_persistence_error():
    error = ResearchPersistenceError("Database failure")

    assert str(error) == "Database failure"