import sys
from collections.abc import AsyncGenerator
from unittest.mock import MagicMock

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from backend.app.database.session import async_session_factory
from backend.app.main import app

sys.modules["streamlit"] = MagicMock()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    Async HTTP client for testing FastAPI routes.
    """
    transport = ASGITransport(
        app=app,
        raise_app_exceptions=False,
    )

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client


@pytest_asyncio.fixture
async def async_session():
    async with async_session_factory() as session:
        yield session

        # rollback anything left open
        await session.rollback()
