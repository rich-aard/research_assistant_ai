# sources.py
import streamlit as st


def render_sources():
    """Display the list of sources from the completed research result.

    Must only be called after a research result is available in
    st.session_state.research_result.
    """

    #  Get sources
    result = st.session_state.get("research_result")
    sources = result.get("sources", []) if result else []

    #  Empty state
    if not sources:
        st.info("No sources were returned.")
        return

    #  Source list
    st.markdown("### Sources")

    for index, source in enumerate(sources, start=1):
        title = source.get("title", "Untitled source")
        url = source.get("url")
        source_type = source.get("source")
        if url:
            st.markdown(f"{index}. [{title}]({url})")
        else:
            st.markdown(f"{index}. {title}")

        if source_type:
            st.caption(f"Source type: {source_type}")
