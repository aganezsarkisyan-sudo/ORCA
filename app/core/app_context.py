from __future__ import annotations

import asyncio
import uuid
from typing import Any

from app.api.dolphin.client import DolphinClient
from app.repositories.dolphin_repository import DolphinRepository
from app.repositories.account_repository import AccountRepository
from app.repositories.excel_mapping_repository import ExcelMappingRepository
from app.repositories.history_repository import HistoryRepository
from app.services.dolphin_service import DolphinService
from app.controllers.dolphin_controller import DolphinController
from app.services.mapping_service import MappingService
from app.services.excel_mapping_service import ExcelMappingService
from app.database.database import init_db
from app.core.config import settings


class AppContext:
    """Holds app-wide services and controllers.

    Construct once at startup and pass to UI/MainWindow.
    """

    def __init__(self) -> None:
        self.operation_id = None
        self.loop = asyncio.get_event_loop()

        # Initialize DB (create tables)
        init_db()

        # Build core components
        self.dolphin_client = DolphinClient(base_url=settings.dolphin_base_url, api_token=settings.dolphin_api_token, timeout=settings.dolphin_timeout, retry_count=settings.dolphin_retry_count)
        self.dolphin_repo = DolphinRepository(self.dolphin_client)
        self.account_repo = AccountRepository()
        self.dolphin_service = DolphinService(self.dolphin_repo)
        self.dolphin_controller = DolphinController(self.dolphin_service)

        # Excel mapping
        self.excel_repo = ExcelMappingRepository()
        self.mapping_service = MappingService()
        self.excel_mapping_service = ExcelMappingService(self.excel_repo, None, self.mapping_service)

    def new_operation(self) -> str:
        self.operation_id = str(uuid.uuid4())
        return self.operation_id


app_context: AppContext | None = None


def get_app_context() -> AppContext:
    global app_context
    if app_context is None:
        app_context = AppContext()
    return app_context
