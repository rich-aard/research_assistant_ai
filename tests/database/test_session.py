from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import session


def test_engine_uses_configured_database_url():
    assert str(session.engine.url) == session.settings.database_url


def test_async_session_factory_is_configured():
    factory = session.async_session_factory

    assert factory.kw["bind"] is session.engine
    assert factory.kw["expire_on_commit"] is False


@pytest.mark.asyncio
async def test_get_session_yields_async_session(mocker):
    mock_session = AsyncMock(spec=AsyncSession)

    session_context = mocker.MagicMock()
    session_context.__aenter__ = AsyncMock(return_value=mock_session)
    session_context.__aexit__ = AsyncMock(return_value=None)

    mocker.patch(
        "backend.app.database.session.async_session_factory",
        return_value=session_context,
    )

    generator = session.get_session()

    result = await anext(generator)

    assert result is mock_session

    await generator.aclose()

    session_context.__aenter__.assert_awaited_once()
    session_context.__aexit__.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_session_closes_session(mocker):
    mock_session = AsyncMock(spec=AsyncSession)

    session_context = mocker.MagicMock()
    session_context.__aenter__ = AsyncMock(return_value=mock_session)
    session_context.__aexit__ = AsyncMock(return_value=None)

    mocker.patch(
        "backend.app.database.session.async_session_factory",
        return_value=session_context,
    )

    async with session.async_session_factory() as db_session:
        assert db_session is mock_session

    session_context.__aexit__.assert_awaited_once()
