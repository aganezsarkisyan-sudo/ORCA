"""Statistics service: synchronization and statistics operations."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable
from loguru import logger

from app.repositories.dolphin_repository import DolphinRepository
from app.repositories.account_repository import AccountRepository
from app.repositories.mapping_repository import MappingRepository
from app.repositories.history_repository import HistoryRepository
from app.services.mapping_service import MappingService


class StatisticsService:
    """Service responsible for synchronizing Dolphin accounts into local DB and
    managing statistics storage.
    """

    def __init__(self, dolphin_repo: DolphinRepository, account_repo: AccountRepository, mapping_repo: MappingRepository, history_repo: HistoryRepository, mapping_service: MappingService) -> None:
        self._dolphin = dolphin_repo
        self._accounts = account_repo
        self._mapping = mapping_repo
        self._history = history_repo
        self._matcher = mapping_service

    async def synchronize_accounts(self) -> dict:
        """Synchronize accounts from Dolphin into local DB.

        - Insert new accounts
        - Update existing accounts
        - Disable missing accounts
        - Do not delete records
        Returns summary dict.
        """
        started = datetime.utcnow()
        entry = self._history.create_entry(started_at=started)
        processed = 0
        success = 0
        failed = 0
        errors: list[str] = []

        try:
            remote_accounts = await self._dolphin.get_accounts()
            processed = len(remote_accounts)

            # Build candidate list for matching (dolphin_id, dolphin_name)
            candidates = [(a.id, a.id, a.name) for a in remote_accounts]

            local_accounts = self._accounts.get_all()
            local_map = {la.dolphin_id: la for la in local_accounts}

            # Insert or update
            for ra in remote_accounts:
                try:
                    existing = local_map.get(str(ra.id))
                    if existing is None:
                        # insert
                        acct = self._accounts.save_account(dolphin_id=str(ra.id), dolphin_name=ra.name, display_name=ra.name, status=ra.status, account_status=ra.account_status, campaign_status=ra.campaign_status, adset_status=ra.adset_status, currency=ra.currency, timezone=ra.timezone, balance=ra.balance)
                        logger.info("Synchronized: inserted dolphin_id={dolphin_id} as local id={id}", dolphin_id=ra.id, id=acct.id)
                    else:
                        # update
                        self._accounts.update_account(existing.id, dolphin_name=ra.name, display_name=ra.name, status=ra.status, account_status=ra.account_status, campaign_status=ra.campaign_status, adset_status=ra.adset_status, currency=ra.currency, timezone=ra.timezone, balance=ra.balance, enabled=True)
                        logger.info("Synchronized: updated dolphin_id={dolphin_id} local id={id}", dolphin_id=ra.id, id=existing.id)
                    success += 1
                except Exception as exc:
                    logger.exception("Failed to sync account {id}", id=ra.id)
                    failed += 1
                    errors.append(str(exc))

            # Disable missing accounts
            remote_ids = {str(a.id) for a in remote_accounts}
            for la in local_accounts:
                if la.dolphin_id not in remote_ids and la.enabled:
                    self._accounts.update_account(la.id, enabled=False)
                    logger.info("Disabled local account id={id} dolphin_id={dolphin_id} because missing remotely", id=la.id, dolphin_id=la.dolphin_id)

            # Optionally perform mapping attempts for unmatched accounts (example: batch)
            # Here we just log mapping confidence for display name candidates
            candidate_tuples = [(int(la.id), la.dolphin_id, la.dolphin_name or la.display_name) for la in local_accounts]
            for la in local_accounts:
                res = self._matcher.match(la.display_name or "", candidate_tuples)
                logger.debug("Mapping check for local {local} -> {res}", local=la.display_name, res=res)

        except Exception as exc:
            logger.exception("Synchronization failed")
            errors.append(str(exc))
        finally:
            finished = datetime.utcnow()
            self._history.finalize_entry(entry.id, finished_at=finished, accounts_processed=processed, accounts_success=success, accounts_failed=failed, errors=("\n".join(errors) if errors else None))

        return {"processed": processed, "success": success, "failed": failed, "errors": errors}

    async def store_statistics(self, stats: Iterable[dict]) -> int:
        # Delegate to statistics repository (not implemented here to avoid duplication)
        from app.repositories.statistics_repository import StatisticsRepository

        repo = StatisticsRepository()
        return repo.add_statistics(stats)
