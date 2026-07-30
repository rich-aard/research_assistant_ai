import pytest
from pydantic import ValidationError

from backend.app.models.writer import WriterOutput


def test_writer_output_valid():
    output = WriterOutput(
        report="# Research Report\n\nThis is the report.",
        summary="This is a concise summary of the research.",
    )

    assert output.report == "# Research Report\n\nThis is the report."
    assert output.summary == "This is a concise summary of the research."


def test_writer_output_requires_report():
    with pytest.raises(ValidationError):
        WriterOutput(
            summary="This is a summary.",
        )


def test_writer_output_requires_summary():
    with pytest.raises(ValidationError):
        WriterOutput(
            report="# Research Report",
        )


def test_writer_output_model_dump():
    output = WriterOutput(
        report="# Research Report",
        summary="Research summary.",
    )

    assert output.model_dump() == {
        "report": "# Research Report",
        "summary": "Research summary.",
    }