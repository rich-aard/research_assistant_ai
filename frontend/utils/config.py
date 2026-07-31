from os import getenv
from urllib.parse import urljoin


def get_api_base_url() -> str:
    """Return the API base URL from environment or fallback."""
    url = getenv("API_BASE_URL")
    if not url:
        url = "http://localhost:8000"
    return url.rstrip("/")


API_BASE_URL = get_api_base_url()
RESEARCH_ENDPOINT = urljoin(API_BASE_URL + "/", "research")
