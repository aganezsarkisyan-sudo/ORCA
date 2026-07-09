"""Repository for sync history entries."""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from loguru import logger

from app.database.models import SyncHistory
from app.database.session import get_session


class HistoryRepository:
    def __init__(self, session_factory=get_session) -> None:
        self._session_factory = session_factory

    def create_entry(self, started_at: datetime | None = None) -> SyncHistory:
        started_at = started_at or datetime.utcnow()
        with self._session_factory() as session:
            entry = SyncHistory(started_at=started_at)
            session.add(entry)
            session.flush()
            logger.info("Created sync history id={id} started_at={started}", id=entry.id, started=entry.started_at)
            return entry

    def finalize_entry(self, entry_id: int, finished_at: datetime | None = None, accounts_processed: int = 0, accounts_success: int = 0, accounts_failed: int = 0, errors: str | None = None) -> SyncHistory:
        finished_at = finished_at or datetime.utcnow()
        with self._session_factory() as session:
            entry = session.get(SyncHistory, entry_id)
            if entry is None:
                raise ValueError("SyncHistory entry not found")
            entry.finished_at = finished_at
            entry.duration = (entry.finished_at - entry.started_at).total_seconds()
            entry.accounts_processed = accounts_processed
            entry.accounts_success = accounts_success
            entry.accounts_failed = accounts_failed
            entry.errors = errors
            session.add(entry)
            logger.info("Finalized sync history id={id} processed={proc} success={s} failed={f}", id=entry.id, proc=accounts_processed, s=accounts_success, f=accounts_failed)
            return entry
