"""
Centralized logging using loguru
"""
import sys
from pathlib import Path
from loguru import logger
from typing import Optional
from framework.core.config_manager import config


def _redact_log_record(record):
    from framework.utils.redact import redact_log_message
    record["message"] = redact_log_message(record["message"])
    return True


class Logger:
    """Centralized logger configuration"""

    _configured = False
    _handler_ids: list = []

    @staticmethod
    def setup(
        log_level: Optional[str] = None,
        log_file: Optional[str] = None,
        rotation: str = "10 MB",
        retention: str = "7 days",
        force: bool = False,
    ):
        """Configure loguru logger."""
        if Logger._configured and not force:
            return

        if force:
            Logger.reset_for_tests()

        logger.remove()

        level = log_level or config.base.log_level
        log_path = Path(log_file or config.base.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        stdout_id = logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=level,
            colorize=True,
            filter=_redact_log_record,
        )
        file_id = logger.add(
            log_path,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=level,
            rotation=rotation,
            retention=retention,
            compression="zip",
            enqueue=True,
            filter=_redact_log_record,
        )
        Logger._handler_ids = [stdout_id, file_id]
        Logger._configured = True

    @staticmethod
    def reset_for_tests():
        """Reset logger configuration for unit tests."""
        for handler_id in Logger._handler_ids:
            try:
                logger.remove(handler_id)
            except ValueError:
                pass
        Logger._handler_ids = []
        Logger._configured = False

    @staticmethod
    def get_logger(name: str = None):
        if not Logger._configured:
            Logger.setup()
        return logger.bind(name=name) if name else logger


Logger.setup()
log = Logger.get_logger(__name__)
