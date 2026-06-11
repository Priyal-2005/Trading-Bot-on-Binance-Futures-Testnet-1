"""Logging configuration for the trading bot.

Sets up structured logging with both file and console handlers.
File handler logs to logs/trading.log at INFO level.
Console handler outputs at WARNING level to avoid cluttering CLI output.
"""

import logging
import os
from pathlib import Path


_LOG_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
_LOG_FILE: str = os.path.join(_LOG_DIR, "trading.log")

_LOG_FORMAT: str = (
    "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
)
_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"


def setup_logging() -> logging.Logger:
    """Configure and return the root logger for the trading bot.

    Creates the logs directory if it does not exist. Attaches a file
    handler (INFO level) and a console handler (WARNING level) so that
    routine log lines go to the file while only errors and warnings
    surface on the terminal.

    Returns:
        logging.Logger: The configured root logger named ``trading_bot``.
    """
    Path(_LOG_DIR).mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("trading_bot")
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers on repeated calls
    if logger.handlers:
        return logger

    # --- File handler (INFO+) ---
    file_handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))

    # --- Console handler (WARNING+) ---
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
