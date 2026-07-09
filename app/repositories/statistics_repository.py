"""Statistics repository: store daily statistics without overwriting history."""
from __future__ import annotations

from typing import Iterable
from datetime import datetime
from loguru import logger

from sqlalchemy.orm import Session

from app.database.models import DailyStatistics
from app.database.session import get_session


class StatisticsRepository:
    def __init__(self, session_factory=get_session) -> None:
        self._session_factory = session_factory

    def add_statistics(self, stats: Iterable[dict]) -> int:
        """Insert statistics rows; never overwrite existing history.

        stats: iterable of dicts with keys account_id, date, spend, cpl, clicks, impressions, payment_info, status
        Returns number of inserted rows.
        """
        inserted = 0
        with self._session_factory() as session:
            for s in stats:
                row = DailyStatistics(
                    account_id=s["account_id"],
                    date=s["date"],
                    spend=s.get("spend"),
                    cpl=s.get("cpl"),
                    clicks=s.get("clicks"),
                    impressions=s.get("impressions"),
                    payment_info=s.get("payment_info"),
                    status=s.get("status"),
                    created_at=datetime.utcnow(),
                )
                session.add(row)
                inserted += 1
            logger.info("Inserted {n} statistics rows", n=inserted)
        return inserted

    def list_for_account(self, account_id: int) -> list[DailyStatistics]:
        with self._session_factory() as session:
            return session.query(DailyStatistics).filter(DailyStatistics.account_id == account_id).all()
