from frontend.app.components.results import render_results


def test_render_results_without_result(mocker):
    mocker.patch(
        "frontend.app.components.results.st.session_state",
        {},
    )

    error = mocker.patch(
        "frontend.app.components.results.st.error",
    )
    button = mocker.patch(
        "frontend.app.components.results.st.button",
        return_value=False,
    )

    render_results()

    error.assert_called_once_with(
        "No research result found. Please start a new research."
    )
    button.assert_called_once_with("Go to Research")


def test_render_results_with_result(mocker):
    result = {
        "topic": "Artificial Intelligence",
        "summary": "Research summary.",
        "report": "# Research Report",
        "sources": [
            {
                "title": "Example Source",
                "url": "https://example.com",
                "source": "tavily",
            }
        ],
    }

    mocker.patch(
        "frontend.app.components.results.st.session_state",
        {"research_result": result},
    )

    title = mocker.patch(
        "frontend.app.components.results.st.title",
    )
    subheader = mocker.patch(
        "frontend.app.components.results.st.subheader",
    )
    markdown = mocker.patch(
        "frontend.app.components.results.st.markdown",
    )

    mocker.patch(
        "frontend.app.components.results.st.info",
    )
    mocker.patch(
        "frontend.app.components.results.st.caption",
    )
    mocker.patch(
        "frontend.app.components.results.st.divider",
    )
    mocker.patch(
        "frontend.app.components.results.st.button",
        return_value=False,
    )

    render_results()

    title.assert_called_once_with("Research Results")
    subheader.assert_called_once_with("Artificial Intelligence")

    markdown.assert_any_call("### Summary")
    markdown.assert_any_call("# Research Report")
    markdown.assert_any_call("### Sources")
    markdown.assert_any_call("1. [Example Source](https://example.com)")


def test_render_results_without_sources(mocker):
    result = {
        "topic": "AI",
        "summary": "Summary",
        "report": "Report",
        "sources": [],
    }

    mocker.patch(
        "frontend.app.components.results.st.session_state",
        {"research_result": result},
    )

    info = mocker.patch(
        "frontend.app.components.results.st.info",
    )

    mocker.patch(
        "frontend.app.components.results.st.title",
    )
    mocker.patch(
        "frontend.app.components.results.st.subheader",
    )
    mocker.patch(
        "frontend.app.components.results.st.markdown",
    )
    mocker.patch(
        "frontend.app.components.results.st.divider",
    )
    mocker.patch(
        "frontend.app.components.results.st.button",
        return_value=False,
    )

    render_results()

    info.assert_any_call("No sources were returned.")


def test_start_new_research_clears_state(
    mocker,
    session_state,
):
    result = {
        "topic": "AI",
        "summary": "Summary",
        "report": "Report",
        "sources": [],
    }

    session_state.update(
        {
            "research_id": "123",
            "research_state": {},
            "progress_data": {},
            "research_result": result,
            "listener_started": True,
            "page": "results",
        }
    )

    mocker.patch(
        "frontend.app.components.results.st.session_state",
        session_state,
    )

    mocker.patch(
        "frontend.app.components.results.st.title",
    )
    mocker.patch(
        "frontend.app.components.results.st.subheader",
    )
    mocker.patch(
        "frontend.app.components.results.st.markdown",
    )
    mocker.patch(
        "frontend.app.components.results.st.info",
    )
    mocker.patch(
        "frontend.app.components.results.st.caption",
    )
    mocker.patch(
        "frontend.app.components.results.st.divider",
    )

    button = mocker.patch(
        "frontend.app.components.results.st.button",
        return_value=True,
    )

    rerun = mocker.patch(
        "frontend.app.components.results.st.rerun",
    )

    render_results()

    button.assert_called_once_with(
        "Start New Research",
        type="primary",
    )

    assert "research_id" not in session_state
    assert "research_state" not in session_state
    assert "progress_data" not in session_state
    assert "research_result" not in session_state
    assert "listener_started" not in session_state

    assert session_state["page"] == "form"
    rerun.assert_called_once()
