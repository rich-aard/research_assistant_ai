import logging
from logging.handlers import RotatingFileHandler

from backend.app.core.config import settings

LOG_DIR = settings.base_dir / "logs"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _get_log_level() -> int:
    """
    Reads LOG_LEVEL from environment, defaults to INFO.
    """
    level = getattr(logging, settings.log_level, None)

    if not isinstance(level, int):
        logging.warning(
            "Invalid LOG_LEVEL '%s', falling back to INFO.",
            settings.log_level,
        )
        return logging.INFO
    return level


def _build_formatter() -> logging.Formatter:
    return logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)


def _build_file_handler(log_level: int) -> RotatingFileHandler:
    """
    Create a rotating file handler and ensure the log directory exists.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    handler = RotatingFileHandler(
        LOG_DIR / "research_assistant.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    handler.setFormatter(_build_formatter())
    handler.setLevel(log_level)
    return handler


def _build_console_handler(log_level: int) -> logging.StreamHandler:
    handler = logging.StreamHandler()
    handler.setFormatter(_build_formatter())
    handler.setLevel(log_level)
    return handler


def setup_logging() -> None:
    """
    Configure the application's root logger.

    This function should be called once during application startup.
    It attaches console and rotating file handlers if they have not
    already been configured.
    """
    root_logger = logging.getLogger()

    if root_logger.handlers:
        return

    log_level = _get_log_level()
    root_logger.setLevel(log_level)

    root_logger.addHandler(_build_file_handler(log_level))
    root_logger.addHandler(_build_console_handler(log_level))


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
