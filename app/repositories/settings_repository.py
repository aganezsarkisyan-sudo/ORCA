from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from loguru import logger

from app.database.session import get_session
from app.database.models import Settings


class SettingsRepository:
    def __init__(self, session_factory=get_session) -> None:
        self._session_factory = session_factory

    def get(self) -> Optional[Settings]:
        with self._session_factory() as session:
            return session.query(Settings).first()

    def save(self, **kwargs) -> Settings:
        with self._session_factory() as session:
            s = session.query(Settings).first()
            if s is None:
                s = Settings(**kwargs)
                session.add(s)
                session.flush()
                logger.info("Created settings")
                return s
            for k, v in kwargs.items():
                if hasattr(s, k):
                    setattr(s, k, v)
            session.add(s)
            logger.info("Updated settings")
            return s
