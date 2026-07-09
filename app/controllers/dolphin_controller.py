"""Controller layer for Dolphin integration.

Controllers mediate between UI and Services. They return view models suitable
for presentation and never perform IO directly.
"""
from __future__ import annotations

from dataclasses import asdict
from typing import Any

from app.services.dolphin_service import DolphinService, AccountViewModel, DashboardSummary


class DolphinController:
    """Controller used by the UI to interact with Dolphin features."""

    def __init__(self, service: DolphinService) -> None:
        self._service = service

    async def check_connection(self) -> dict[str, Any]:
        healthy = await self._service.check_connection()
        return {"ok": healthy}

    async def get_accounts(self, *args, **kwargs) -> list[dict]:
        accounts = await self._service.load_accounts(*args, **kwargs)
        return [asdict(a) for a in accounts]

    async def get_statistics(self, *args, **kwargs) -> list[dict]:
        stats = await self._service.load_statistics(*args, **kwargs)
        # statistics are DTO dataclasses — convert to dict for UI consumption
        return [asdict(s) for s in stats]

    async def get_dashboard(self) -> dict:
        summary: DashboardSummary = await self._service.load_dashboard()
        return asdict(summary)
