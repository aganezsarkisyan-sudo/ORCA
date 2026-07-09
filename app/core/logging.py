from __future__ import annotations

from loguru import logger
import sys


def setup_logging() -> None:
    """Configure loguru for simple console + file logging."""
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    logger.add("logs/orca.log", rotation="10 MB", level="DEBUG")
