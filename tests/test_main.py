from unittest.mock import Mock

import pytest

from backend.app import main


@pytest.mark.asyncio
async def test_lifespan_creates_required_directories(mocker):
    setup_logging = mocker.patch(
        "backend.app.main.setup_logging",
    )

    logger = Mock()
    mocker.patch(
        "backend.app.main.get_logger",
        return_value=logger,
    )

    mkdir = mocker.patch(
        "pathlib.Path.mkdir",
    )

    async with main.lifespan(main.app):
        pass

    setup_logging.assert_called_once()

    logger.info.assert_any_call(
        "Starting %s",
        main.settings.app_name,
    )
    logger.info.assert_any_call(
        "Shutting down %s",
        main.settings.app_name,
    )

    assert mkdir.call_count == 5


def test_app_configuration():
    assert main.app.title == main.settings.app_name
    assert main.app.version == main.settings.app_version
    assert main.app.debug == main.settings.debug


def test_app_has_required_routes():
    health_paths = {
        route.path for route in main.health_router.routes if hasattr(route, "path")
    }

    research_paths = {
        route.path for route in main.research_router.routes if hasattr(route, "path")
    }

    assert "/health" in health_paths
    assert "/research" in research_paths
    assert "/research/{research_id}" in research_paths
    assert "/research/{research_id}/stream" in research_paths


def test_cors_middleware_is_configured():
    middleware_classes = {middleware.cls for middleware in main.app.user_middleware}

    assert main.CORSMiddleware in middleware_classes
