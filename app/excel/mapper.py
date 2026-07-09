"""Mapper: match Excel blocks to local accounts and persist anchor mapping.

Uses existing MappingService for name matching. Saves mapping into DB using
MappingRepository (which now stores anchor_cell instead of per-field cells).
"""
from __future__ import annotations

from typing import Iterable, List
from loguru import logger

from app.excel.workbook import ExcelBlock
from app.services.mapping_service import MappingService, MappingResult
from app.repositories.mapping_repository import MappingRepository
from app.repositories.account_repository import AccountRepository


class ExcelMapper:
    def __init__(self, mapping_repo: MappingRepository, account_repo: AccountRepository, matcher: MappingService) -> None:
        self._mapping_repo = mapping_repo
        self._account_repo = account_repo
        self._matcher = matcher

    def map_blocks(self, blocks: Iterable[ExcelBlock]) -> List[MappingResult]:
        # gather local accounts: (id, display_name)
        local_accounts = self._account_repo.get_all()
        local_tuples = [(int(a.id), a.display_name or a.dolphin_name or "") for a in local_accounts]

        # candidates for matcher: (account_id, dolphin_id, dolphin_name)
        candidates = [(int(a.id), a.dolphin_id, a.dolphin_name or a.display_name or "") for a in local_accounts]

        results: List[MappingResult] = []
        for block in blocks:
            res = self._matcher.match(block.name, candidates)
            # If confidence is good enough, persist mapping
            if res.account_id is not None and res.confidence >= 0.5:
                try:
                    # create mapping with anchor_cell
                    self._mapping_repo.create(account_id=res.account_id, excel_block_name=block.name, anchor_cell=block.anchor_cell, enabled=True)
                    logger.info("Saved mapping: block={block} -> account_id={aid} confidence={conf}", block=block.name, aid=res.account_id, conf=res.confidence)
                except Exception as exc:
                    logger.exception("Failed to save mapping for block {block}", block=block.name)
            else:
                logger.info("No confident mapping for block {block} (confidence={conf})", block=block.name, conf=res.confidence)
            results.append(res)
        return results
