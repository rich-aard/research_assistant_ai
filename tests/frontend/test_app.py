from unittest.mock import MagicMock

from frontend.app import app

if not hasattr(app, "st"):
    app.st = MagicMock()


def test_main_initializes_page(mocker, session_state):
    mocker.patch.object(
        app.st,
        "session_state",
        session_state,
    )
    mocker.patch.object(app.st, "set_page_config")

    mock_form = mocker.patch.object(
        app,
        "render_research_form",
    )

    app.main()

    assert session_state["page"] == "form"
    mock_form.assert_called_once()


def test_main_routes_to_form(mocker, session_state):
    session_state["page"] = "form"

    mocker.patch.object(
        app.st,
        "session_state",
        session_state,
    )
    mocker.patch.object(app.st, "set_page_config")

    mock_form = mocker.patch.object(app, "render_research_form")
    mock_progress = mocker.patch.object(app, "render_progress")
    mock_results = mocker.patch.object(app, "render_results")

    app.main()

    mock_form.assert_called_once()
    mock_progress.assert_not_called()
    mock_results.assert_not_called()


def test_main_routes_to_progress(mocker, session_state):
    session_state["page"] = "progress"

    mocker.patch.object(
        app.st,
        "session_state",
        session_state,
    )
    mocker.patch.object(app.st, "set_page_config")

    mock_form = mocker.patch.object(app, "render_research_form")
    mock_progress = mocker.patch.object(app, "render_progress")
    mock_results = mocker.patch.object(app, "render_results")

    app.main()

    mock_form.assert_not_called()
    mock_progress.assert_called_once()
    mock_results.assert_not_called()


def test_main_routes_to_results(mocker, session_state):
    session_state["page"] = "results"

    mocker.patch.object(
        app.st,
        "session_state",
        session_state,
    )
    mocker.patch.object(app.st, "set_page_config")

    mock_form = mocker.patch.object(app, "render_research_form")
    mock_progress = mocker.patch.object(app, "render_progress")
    mock_results = mocker.patch.object(app, "render_results")

    app.main()

    mock_form.assert_not_called()
    mock_progress.assert_not_called()
    mock_results.assert_called_once()


def test_main_handles_invalid_page(mocker, session_state):
    session_state["page"] = "invalid"

    mocker.patch.object(
        app.st,
        "session_state",
        session_state,
    )
    mocker.patch.object(app.st, "set_page_config")

    mock_form = mocker.patch.object(app, "render_research_form")
    mock_progress = mocker.patch.object(app, "render_progress")
    mock_results = mocker.patch.object(app, "render_results")

    app.main()

    assert session_state["page"] == "form"
    mock_form.assert_called_once()
    mock_progress.assert_not_called()
    mock_results.assert_not_called()


def test_main_configures_page(mocker, session_state):
    session_state["page"] = "form"

    mocker.patch.object(
        app.st,
        "session_state",
        session_state,
    )

    set_page_config = mocker.patch.object(
        app.st,
        "set_page_config",
    )

    mocker.patch.object(app, "render_research_form")

    app.main()

    set_page_config.assert_called_once_with(
        page_title="Deep Research",
        page_icon="🔍",
        layout="wide",
    )
