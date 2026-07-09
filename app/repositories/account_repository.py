"""Account repository for local persistence."""
from __future__ import annotations

from typing import Iterable, Optional
from datetime import datetime
from loguru import logger

from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from app.database.models import Account
from app.database.session import get_session


class AccountRepository:
    def __init__(self, session_factory=get_session) -> None:
        self._session_factory = session_factory

    def save_account(self, dolphin_id: str, dolphin_name: str | None = None, display_name: str | None = None, **kwargs) -> Account:
        with self._session_factory() as session:
            acct = Account(
                dolphin_id=dolphin_id,
                dolphin_name=dolphin_name,
                display_name=display_name or dolphin_name,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                **kwargs,
            )
            session.add(acct)
            session.flush()
            logger.info("Inserted account {dolphin_id} -> id={id}", dolphin_id=dolphin_id, id=acct.id)
            return acct

    def update_account(self, account_id: int, **kwargs) -> Account:
        with self._session_factory() as session:
            acct = session.get(Account, account_id)
            if acct is None:
                raise NoResultFound(f"Account with id={account_id} not found")
            for k, v in kwargs.items():
                if hasattr(acct, k):
                    setattr(acct, k, v)
            acct.updated_at = datetime.utcnow()
            session.add(acct)
            logger.info("Updated account id={id} fields={fields}", id=acct.id, fields=list(kwargs.keys()))
            return acct

    def delete_account(self, account_id: int) -> None:
        with self._session_factory() as session:
            acct = session.get(Account, account_id)
            if acct is None:
                raise NoResultFound(f"Account with id={account_id} not found")
            # Soft-delete: disable
            acct.enabled = False
            acct.updated_at = datetime.utcnow()
            session.add(acct)
            logger.info("Disabled account id={id}", id=account_id)

    def get_all(self) -> list[Account]:
        with self._session_factory() as session:
            return session.query(Account).all()

    def get_by_id(self, account_id: int) -> Optional[Account]:
        with self._session_factory() as session:
            return session.get(Account, account_id)

    def get_by_dolphin_id(self, dolphin_id: str) -> Optional[Account]:
        with self._session_factory() as session:
            return session.query(Account).filter(Account.dolphin_id == dolphin_id).one_or_none()
