import streamlit as st


def render_results() -> None:
    """Presentation-only component that displays the completed research result."""

    result = st.session_state.get("research_result")

    if not result:
        st.error(
            "No research result found. "
            "Please start a new research."
        )

        if st.button("Go to Research"):
            st.session_state.page = "form"
            st.rerun()

        return

    topic = result.get("topic", "Untitled Research")
    summary = result.get("summary")
    report = result.get("report")
    sources = result.get("sources", [])

    st.title("Research Results")
    st.subheader(topic)

    #  Summary 
    if summary:
        st.markdown("### Summary")
        st.info(summary)

    #  Report 
    if report:
        st.markdown("### Report")
        st.markdown(report)

    #  Sources 
    st.markdown("### Sources")

    if sources:
        for index, source in enumerate(sources, start=1):
            title = source.get("title", "Untitled source")
            url = source.get("url")
            source_type = source.get("source")

            if url:
                st.markdown(f"{index}. [{title}]({url})")
            else:
                st.markdown(f"{index}. {title}")

            if source_type:
                st.caption(f"Source: {source_type}")
    else:
        st.info("No sources were returned.")

    #  New research 
    st.divider()

    if st.button("Start New Research", type="primary"):
        # Clear all research-related state
        st.session_state.pop("research_id", None)
        st.session_state.pop("research_state", None)
        st.session_state.pop("progress_data", None)
        st.session_state.pop("research_result", None)
        st.session_state.pop("listener_started", None)

        st.session_state.page = "form"
        st.rerun()
