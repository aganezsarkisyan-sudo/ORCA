"""Database initialization and helper functions."""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings
from loguru import logger

Base = declarative_base()


def get_engine(url: str | None = None, **kwargs):
    url = url or settings.database_url
    logger.debug("Creating engine for URL: {}", url)
    return create_engine(url, future=True, echo=False, **kwargs)


def init_db(engine=None) -> None:
    """Create all tables if they do not exist."""
    engine = engine or get_engine()
    from app.database import models  # noqa: F401 (ensure models are registered)

    logger.info("Initializing database and creating tables if not present")
    Base.metadata.create_all(bind=engine)
