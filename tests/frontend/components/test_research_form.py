from backend.app.models.enums import ResearchDepth
from frontend.components.research_form import render_research_form


def test_research_form_empty_topic(mocker):
    mocker.patch(
        "frontend.components.research_form.st.text_input",
        return_value="",
    )
    mocker.patch(
        "frontend.components.research_form.st.selectbox",
        return_value=3,
    )

    button = mocker.patch(
        "frontend.components.research_form.st.button",
        return_value=True,
    )

    error = mocker.patch(
        "frontend.components.research_form.st.error",
    )

    render_research_form()

    button.assert_called_once()
    error.assert_called_once_with("Please enter a research topic.")


def test_research_form_success(
    mocker,
    session_state,
):
    mocker.patch(
        "frontend.components.research_form.st.text_input",
        return_value="  Artificial Intelligence  ",
    )
    mocker.patch(
        "frontend.components.research_form.st.selectbox",
        return_value=ResearchDepth.STANDARD.value,
    )

    mocker.patch(
        "frontend.components.research_form.st.button",
        return_value=True,
    )

    mock_start = mocker.patch(
        "frontend.components.research_form.start_new_research",
        return_value={
            "research_id": "abc123",
            "status": "queued",
            "stage": "queued",
            "progress": 0,
            "message": "Research started.",
        },
    )

    mocker.patch(
        "frontend.components.research_form.st.session_state",
        session_state,
    )

    mocker.patch(
        "frontend.components.research_form.st.spinner",
    )

    rerun = mocker.patch(
        "frontend.components.research_form.st.rerun",
    )

    render_research_form()

    mock_start.assert_called_once_with(
        topic="Artificial Intelligence",
        depth=ResearchDepth.STANDARD.value,
    )

    assert session_state["research_id"] == "abc123"
    assert session_state["page"] == "progress"
    assert session_state["research_state"]["status"] == "queued"

    rerun.assert_called_once()
