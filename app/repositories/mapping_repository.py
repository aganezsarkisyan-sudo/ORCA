"""Mapping repository CRUD operations."""
from __future__ import annotations

from typing import Optional
from datetime import datetime
from loguru import logger

from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from app.database.models import AccountMapping
from app.database.session import get_session


class MappingRepository:
    def __init__(self, session_factory=get_session) -> None:
        self._session_factory = session_factory

    def create(self, account_id: int, excel_block_name: str, **kwargs) -> AccountMapping:
        with self._session_factory() as session:
            mapping = AccountMapping(account_id=account_id, excel_block_name=excel_block_name, **kwargs)
            session.add(mapping)
            session.flush()
            logger.info("Created mapping id={id} account_id={account_id} block={block}", id=mapping.id, account_id=account_id, block=excel_block_name)
            return mapping

    def update(self, mapping_id: int, **kwargs) -> AccountMapping:
        with self._session_factory() as session:
            mapping = session.get(AccountMapping, mapping_id)
            if mapping is None:
                raise NoResultFound(f"Mapping {mapping_id} not found")
            for k, v in kwargs.items():
                if hasattr(mapping, k):
                    setattr(mapping, k, v)
            session.add(mapping)
            logger.info("Updated mapping id={id} fields={fields}", id=mapping.id, fields=list(kwargs.keys()))
            return mapping

    def delete(self, mapping_id: int) -> None:
        with self._session_factory() as session:
            mapping = session.get(AccountMapping, mapping_id)
            if mapping is None:
                raise NoResultFound(f"Mapping {mapping_id} not found")
            session.delete(mapping)
            logger.info("Deleted mapping id={id}", id=mapping_id)

    def get_by_id(self, mapping_id: int) -> Optional[AccountMapping]:
        with self._session_factory() as session:
            return session.get(AccountMapping, mapping_id)

    def list_for_account(self, account_id: int) -> list[AccountMapping]:
        with self._session_factory() as session:
            return session.query(AccountMapping).filter(AccountMapping.account_id == account_id).all()
