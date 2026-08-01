import requests
import streamlit as st

from backend.app.models.enums import ResearchDepth
from frontend.app.utils.research import start_new_research

VALID_DEPTHS = [depth.value for depth in ResearchDepth]
DEFAULT_DEPTH = ResearchDepth.STANDARD.value


def render_research_form() -> None:
    """Render the research input form and start a new research job."""

    st.title("Research")

    # Inputs
    topic = st.text_input(
        "Research topic",
        placeholder="e.g. Impact of AI on healthcare",
        key="research_topic_input",
    )

    depth = st.selectbox(
        "Research depth",
        options=VALID_DEPTHS,
        index=VALID_DEPTHS.index(DEFAULT_DEPTH),
        key="research_depth_select",
    )

    # Start research
    if not st.button("Start Research", type="primary"):
        return

    #  Validation
    topic = topic.strip()

    if not topic:
        st.error("Please enter a research topic.")
        return

    if depth not in VALID_DEPTHS:
        st.error("Invalid research depth selected.")
        return

    # Start API request
    try:
        with st.spinner("Starting research..."):
            response = start_new_research(
                topic=topic,
                depth=depth,
            )

    except requests.ConnectionError:
        st.error(
            "Unable to connect to the research server. "
            "Please check that the backend is running."
        )
        return

    except requests.HTTPError as exc:
        status_code = (
            exc.response.status_code if exc.response is not None else "unknown"
        )

        st.error(f"Research API returned an error (HTTP {status_code}).")
        return

    except ValueError:
        st.error("The research server returned an invalid response. Please try again.")
        return

    except requests.RequestException as exc:
        st.error(f"A network error occurred while starting research: {exc}")
        return

    # Store research state
    research_id = response["research_id"]

    st.session_state.research_id = research_id

    st.session_state.research_state = {
        "research_id": research_id,
        "status": response.get("status", "queued"),
        "stage": response.get("stage"),
        "progress": response.get("progress", 0),
        "message": response.get(
            "message",
            "Research started.",
        ),
    }

    # Move to progress stage
    st.session_state.page = "progress"

    st.rerun()
