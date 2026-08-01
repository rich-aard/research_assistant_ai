from unittest.mock import call, patch

import streamlit as st

from frontend.app.components.sources import render_sources


def test_no_sources_key_in_result(session_state):
    session_state["research_result"] = {"report": "..."}

    with (
        patch.object(st, "session_state", session_state),
        patch.object(st, "info") as mock_info,
        patch.object(st, "markdown") as mock_markdown,
        patch.object(st, "caption") as mock_caption,
    ):
        render_sources()

    mock_info.assert_called_once_with("No sources were returned.")
    mock_markdown.assert_not_called()
    mock_caption.assert_not_called()


def test_sources_is_none(session_state):
    session_state["research_result"] = {
        "sources": None,
    }

    with (
        patch.object(st, "session_state", session_state),
        patch.object(st, "info") as mock_info,
        patch.object(st, "markdown") as mock_markdown,
    ):
        render_sources()

    mock_info.assert_called_once_with("No sources were returned.")
    mock_markdown.assert_not_called()


def test_empty_source_list(session_state):
    session_state["research_result"] = {
        "sources": [],
    }

    with (
        patch.object(st, "session_state", session_state),
        patch.object(st, "info") as mock_info,
        patch.object(st, "markdown") as mock_markdown,
    ):
        render_sources()

    mock_info.assert_called_once_with("No sources were returned.")
    mock_markdown.assert_not_called()


def test_one_source_with_url(session_state):
    session_state["research_result"] = {
        "sources": [
            {
                "title": "Example",
                "url": "https://example.com",
            }
        ]
    }

    with (
        patch.object(st, "session_state", session_state),
        patch.object(st, "info") as mock_info,
        patch.object(st, "markdown") as mock_markdown,
        patch.object(st, "caption") as mock_caption,
    ):
        render_sources()

    mock_info.assert_not_called()

    mock_markdown.assert_has_calls(
        [
            call("### Sources"),
            call("1. [Example](https://example.com)"),
        ]
    )

    assert mock_markdown.call_count == 2
    mock_caption.assert_not_called()


def test_one_source_without_url(session_state):
    session_state["research_result"] = {
        "sources": [
            {
                "title": "No link",
                "url": None,
            }
        ]
    }

    with (
        patch.object(st, "session_state", session_state),
        patch.object(st, "info") as mock_info,
        patch.object(st, "markdown") as mock_markdown,
    ):
        render_sources()

    mock_info.assert_not_called()

    mock_markdown.assert_has_calls(
        [
            call("### Sources"),
            call("1. No link"),
        ]
    )

    assert mock_markdown.call_count == 2


def test_multiple_sources_numbered(session_state):
    session_state["research_result"] = {
        "sources": [
            {
                "title": "Source A",
                "url": "http://a.com",
            },
            {
                "title": "Source B",
                "url": None,
            },
            {
                "title": "Source C",
                "url": "http://c.com",
            },
        ]
    }

    with (
        patch.object(st, "session_state", session_state),
        patch.object(st, "markdown") as mock_markdown,
    ):
        render_sources()

    mock_markdown.assert_has_calls(
        [
            call("### Sources"),
            call("1. [Source A](http://a.com)"),
            call("2. Source B"),
            call("3. [Source C](http://c.com)"),
        ]
    )

    assert mock_markdown.call_count == 4


def test_missing_title_fallback(session_state):
    session_state["research_result"] = {
        "sources": [
            {
                "url": "http://x.com",
            }
        ]
    }

    with (
        patch.object(st, "session_state", session_state),
        patch.object(st, "markdown") as mock_markdown,
    ):
        render_sources()

    mock_markdown.assert_any_call("1. [Untitled source](http://x.com)")


def test_source_type_present(session_state):
    session_state["research_result"] = {
        "sources": [
            {
                "title": "Test",
                "source": "Wikipedia",
            }
        ]
    }

    with (
        patch.object(st, "session_state", session_state),
        patch.object(st, "caption") as mock_caption,
    ):
        render_sources()

    mock_caption.assert_called_once_with("Source type: Wikipedia")


def test_source_type_missing(session_state):
    session_state["research_result"] = {
        "sources": [
            {
                "title": "Test",
                "url": "http://test.com",
            }
        ]
    }

    with (
        patch.object(st, "session_state", session_state),
        patch.object(st, "caption") as mock_caption,
    ):
        render_sources()

    mock_caption.assert_not_called()
