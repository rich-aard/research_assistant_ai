import logging
from logging.handlers import RotatingFileHandler

import backend.app.core.logging as app_logging


def test_get_log_level_valid(mocker):
    mocker.patch.object(
        app_logging.settings,
        "log_level",
        "DEBUG",
    )

    assert app_logging._get_log_level() == logging.DEBUG


def test_get_log_level_invalid_defaults_to_info(mocker):
    mocker.patch.object(
        app_logging.settings,
        "log_level",
        "INVALID_LEVEL",
    )

    result = app_logging._get_log_level()

    assert result == logging.INFO


def test_build_formatter():
    formatter = app_logging._build_formatter()

    assert isinstance(formatter, logging.Formatter)
    assert formatter._fmt == app_logging.LOG_FORMAT
    assert formatter.datefmt == app_logging.DATE_FORMAT


def test_build_file_handler(tmp_path, mocker):
    mocker.patch.object(
        app_logging,
        "LOG_DIR",
        tmp_path / "logs",
    )

    handler = app_logging._build_file_handler(logging.DEBUG)

    try:
        assert isinstance(handler, RotatingFileHandler)
        assert handler.level == logging.DEBUG
        assert handler.maxBytes == 5 * 1024 * 1024
        assert handler.backupCount == 5
        assert handler.formatter is not None
        assert handler.baseFilename.endswith("research_assistant.log")
    finally:
        handler.close()


def test_build_console_handler():
    handler = app_logging._build_console_handler(logging.WARNING)

    assert isinstance(handler, logging.StreamHandler)
    assert handler.level == logging.WARNING
    assert handler.formatter is not None


def test_setup_logging(mocker):
    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers[:]

    try:
        root_logger.handlers.clear()

        mocker.patch.object(
            app_logging,
            "_get_log_level",
            return_value=logging.DEBUG,
        )

        file_handler = mocker.Mock()
        console_handler = mocker.Mock()

        mocker.patch.object(
            app_logging,
            "_build_file_handler",
            return_value=file_handler,
        )
        mocker.patch.object(
            app_logging,
            "_build_console_handler",
            return_value=console_handler,
        )

        app_logging.setup_logging()

        assert root_logger.level == logging.DEBUG
        assert file_handler in root_logger.handlers
        assert console_handler in root_logger.handlers

    finally:
        root_logger.handlers.clear()
        root_logger.handlers.extend(original_handlers)


def test_setup_logging_skips_when_handlers_exist(mocker):
    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers[:]

    try:
        existing_handler = logging.StreamHandler()
        root_logger.handlers.clear()
        root_logger.addHandler(existing_handler)

        get_level = mocker.patch.object(
            app_logging,
            "_get_log_level",
        )
        build_file = mocker.patch.object(
            app_logging,
            "_build_file_handler",
        )
        build_console = mocker.patch.object(
            app_logging,
            "_build_console_handler",
        )

        app_logging.setup_logging()

        get_level.assert_not_called()
        build_file.assert_not_called()
        build_console.assert_not_called()

        assert root_logger.handlers == [existing_handler]

    finally:
        root_logger.handlers.clear()
        root_logger.handlers.extend(original_handlers)
        existing_handler.close()


def test_get_logger():
    logger = app_logging.get_logger("test.logger")

    assert isinstance(logger, logging.Logger)
    assert logger.name == "test.logger"
