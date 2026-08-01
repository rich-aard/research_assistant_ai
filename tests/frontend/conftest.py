import sys
from unittest.mock import MagicMock

import pytest

sys.modules["streamlit"] = MagicMock()


class MockSessionState(dict):
    """Dictionary supporting both key and attribute access."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc


@pytest.fixture
def session_state(mocker):
    """Provide a mocked Streamlit session state for frontend tests."""
    state = MockSessionState()

    mocker.patch(
        "frontend.app.components.progress.st.session_state",
        state,
    )

    return state
