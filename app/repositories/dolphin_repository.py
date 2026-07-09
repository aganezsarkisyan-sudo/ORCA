"""Repository layer for Dolphin API.

DolphinRepository works with DolphinClient and exposes domain-level models
and caching. It never exposes raw JSON.
"""
from __future__ import annotations

from typing import Optional

from app.api.dolphin import client as dolphin_client, models as dto
from app.api.dolphin import exceptions


class DolphinRepository:
    """Repository that communicates with DolphinClient and caches responses."""

    def __init__(self, client: dolphin_client.DolphinClient) -> None:
        self._client = client
        self._accounts_cache: Optional[list[dto.Account]] = None
        self._statistics_cache: Optional[list[dto.Statistics]] = None
        self._status_cache: Optional[dict] = None

    async def test_connection(self) -> bool:
        return await self._client.test_connection()

    async def get_accounts(self, force_refresh: bool = False) -> list[dto.Account]:
        if self._accounts_cache is None or force_refresh:
            accounts = await self._client.get_accounts()
            self._accounts_cache = accounts
        return list(self._accounts_cache)

    async def get_account(self, account_id: str) -> dto.Account:
        # No cache per-account, but could be added later
        return await self._client.get_account(account_id)

    async def get_statistics(self, account_id: str | None = None, start_date: str | None = None, end_date: str | None = None, force_refresh: bool = False) -> list[dto.Statistics]:
        if self._statistics_cache is None or force_refresh:
            stats = await self._client.get_statistics(account_id=account_id, start_date=start_date, end_date=end_date)
            self._statistics_cache = stats
        # If account_id filter was provided but cache contains other accounts, filter in-memory
        if account_id and self._statistics_cache is not None:
            return [s for s in self._statistics_cache if s.account_id == account_id]
        return list(self._statistics_cache or [])

    async def get_status(self, force_refresh: bool = False) -> dict:
        if self._status_cache is None or force_refresh:
            status = await self._client.get_status()
            self._status_cache = status
        return dict(self._status_cache)
