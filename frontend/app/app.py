import streamlit as st

from frontend.app.components.progress import render_progress
from frontend.app.components.research_form import render_research_form
from frontend.app.components.results import render_results


def main() -> None:
    """Configure the Streamlit app and route to the active page."""

    st.set_page_config(
        page_title="Deep Research",
        page_icon="🔍",
        layout="wide",
    )

    if "page" not in st.session_state:
        st.session_state.page = "form"

    current_page = st.session_state.page

    if current_page == "form":
        render_research_form()

    elif current_page == "progress":
        render_progress()

    elif current_page == "results":
        render_results()

    else:
        st.session_state.page = "form"
        render_research_form()


if __name__ == "__main__":
    main()
