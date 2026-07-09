"""Service layer for Dolphin integration.

Contains business logic such as filtering, sorting, searching, and aggregation.
"""
from __future__ import annotations

from typing import Iterable
from dataclasses import dataclass

from app.repositories.dolphin_repository import DolphinRepository
from app.api.dolphin import models as dto


@dataclass(slots=True)
class AccountViewModel:
    id: str
    name: str
    status: str | None
    balance: float | None
    spend: float | None


@dataclass(slots=True)
class DashboardSummary:
    total_accounts: int
    total_spend: float
    total_balance: float


class DolphinService:
    """Service encapsulates business logic for Dolphin data."""

    def __init__(self, repository: DolphinRepository) -> None:
        self._repo = repository

    async def check_connection(self) -> bool:
        return await self._repo.test_connection()

    async def load_accounts(self, search: str | None = None, sort_by: str | None = None, only_active: bool = False) -> list[AccountViewModel]:
        accounts = await self._repo.get_accounts()

        # Searching
        if search:
            accounts = [a for a in accounts if search.lower() in (a.name or "").lower() or search.lower() in (a.id or "").lower()]

        # Filtering
        if only_active:
            accounts = [a for a in accounts if (a.status or "").upper() == "ACTIVE"]

        # Sorting
        if sort_by == "spend":
            accounts.sort(key=lambda a: (a.spend or 0.0), reverse=True)
        elif sort_by == "balance":
            accounts.sort(key=lambda a: (a.balance or 0.0), reverse=True)

        return [AccountViewModel(id=a.id, name=a.name, status=a.status, balance=a.balance, spend=a.spend) for a in accounts]

    async def load_statistics(self, account_id: str | None = None, start_date: str | None = None, end_date: str | None = None) -> list[dto.Statistics]:
        return await self._repo.get_statistics(account_id=account_id, start_date=start_date, end_date=end_date)

    async def load_dashboard(self) -> DashboardSummary:
        accounts = await self._repo.get_accounts()
        total_accounts = len(accounts)
        total_spend = sum((a.spend or 0.0) for a in accounts)
        total_balance = sum((a.balance or 0.0) for a in accounts)
        return DashboardSummary(total_accounts=total_accounts, total_spend=total_spend, total_balance=total_balance)
