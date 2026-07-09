"""Excel mapping repository for the new excel_mapping table."""
from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from loguru import logger

from sqlalchemy.exc import NoResultFound
from app.database.session import get_session
from app.database.models import ExcelMapping


class ExcelMappingRepository:
    def __init__(self, session_factory=get_session) -> None:
        self._session_factory = session_factory

    def create(self, account_id: int, worksheet: str, anchor_cell: str, template_version: str | None = None) -> ExcelMapping:
        with self._session_factory() as session:
            mapping = ExcelMapping(account_id=account_id, worksheet=worksheet, anchor_cell=anchor_cell, template_version=template_version, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
            session.add(mapping)
            session.flush()
            logger.info("Created excel mapping id={id} account_id={aid} anchor={anchor}", id=mapping.id, aid=account_id, anchor=anchor_cell)
            return mapping

    def update(self, mapping_id: int, **kwargs) -> ExcelMapping:
        with self._session_factory() as session:
            mapping = session.get(ExcelMapping, mapping_id)
            if mapping is None:
                raise NoResultFound("ExcelMapping not found")
            for k, v in kwargs.items():
                if hasattr(mapping, k):
                    setattr(mapping, k, v)
            mapping.updated_at = datetime.utcnow()
            session.add(mapping)
            logger.info("Updated excel mapping id={id}", id=mapping.id)
            return mapping

    def get_by_account(self, account_id: int) -> List[ExcelMapping]:
        with self._session_factory() as session:
            return session.query(ExcelMapping).filter(ExcelMapping.account_id == account_id).all()

    def get_by_anchor(self, worksheet: str, anchor_cell: str) -> Optional[ExcelMapping]:
        with self._session_factory() as session:
            return session.query(ExcelMapping).filter(ExcelMapping.worksheet == worksheet, ExcelMapping.anchor_cell == anchor_cell).one_or_none()

    def list_by_worksheet(self, worksheet: str) -> List[ExcelMapping]:
        with self._session_factory() as session:
            return session.query(ExcelMapping).filter(ExcelMapping.worksheet == worksheet).all()
