"""Service to manage Excel mappings and compatibility with legacy mapping table."""
from __future__ import annotations

from typing import List
from datetime import datetime
from loguru import logger

from app.repositories.excel_mapping_repository import ExcelMappingRepository
from app.repositories import mapping_repository as legacy_repo_module
from app.repositories.mapping_repository import MappingRepository
from app.services.mapping_service import MappingService
from app.database.models import AccountMapping as LegacyAccountMapping


class ExcelMappingService:
    def __init__(self, excel_repo: ExcelMappingRepository, mapping_repo: MappingRepository, matcher: MappingService) -> None:
        self._excel_repo = excel_repo
        self._mapping_repo = mapping_repo
        self._matcher = matcher

    def import_legacy_mappings(self) -> int:
        """Read old mappings from account_mapping table (legacy) and create ExcelMapping entries when possible.

        Returns number of migrated rows.
        """
        migrated = 0
        # Use mapping_repo to list existing legacy mappings
        legacy_list = self._mapping_repo.list_all() if hasattr(self._mapping_repo, "list_all") else []
        for lm in legacy_list:
            try:
                if getattr(lm, "anchor_cell", None):
                    # create new excel mapping with worksheet unknown (None) until scanner runs
                    self._excel_repo.create(account_id=lm.account_id, worksheet=lm.excel_block_name or "", anchor_cell=lm.anchor_cell or "")
                    migrated += 1
            except Exception:
                logger.exception("Failed to migrate legacy mapping id={id}", id=lm.id)
        logger.info("Migrated {n} legacy mappings to excel_mapping", n=migrated)
        return migrated

    def ensure_mapping_for_block(self, account_id: int, worksheet: str, anchor_cell: str, template_version: str | None = None):
        # idempotent create or update
        existing = self._excel_repo.get_by_anchor(worksheet, anchor_cell)
        if existing:
            return self._excel_repo.update(existing.id, account_id=account_id, template_version=template_version)
        return self._excel_repo.create(account_id=account_id, worksheet=worksheet, anchor_cell=anchor_cell, template_version=template_version)
