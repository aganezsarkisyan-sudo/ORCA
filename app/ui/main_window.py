from __future__ import annotations

import asyncio
from typing import Final

from qasync import asyncSlot
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QStackedWidget,
    QStatusBar,
    QPushButton,
    QToolBar,
)
from PySide6.QtCore import Qt

from app.ui.widgets.navigation import Navigation
from app.ui.dashboard.page import DashboardPage
from app.ui.accounts.page import AccountsPage
from app.ui.preview.page import PreviewPage
from app.ui.excel.page import ExcelPage
from app.ui.history.page import HistoryPage
from app.ui.settings.page import SettingsPage
from app.core.app_context import get_app_context, AppContext


class MainWindow(QMainWindow):
    PAGE_DASHBOARD: Final[int] = 0
    PAGE_ACCOUNTS: Final[int] = 1
    PAGE_PREVIEW: Final[int] = 2
    PAGE_EXCEL: Final[int] = 3
    PAGE_HISTORY: Final[int] = 4
    PAGE_SETTINGS: Final[int] = 5

    def __init__(self, context: AppContext) -> None:
        super().__init__()
        self.context = context
        self.setWindowTitle("ORCA")
        self.resize(1200, 800)

        self._central = QWidget()
        self.setCentralWidget(self._central)

        layout = QHBoxLayout(self._central)
        layout.setContentsMargins(0, 0, 0, 0)

        # Navigation
        self.navigation = Navigation()
        layout.addWidget(self.navigation, 0)

        # Pages
        self.stack = QStackedWidget()
        self.dashboard_page = DashboardPage(context)
        self.accounts_page = AccountsPage(context)
        self.preview_page = PreviewPage(context)
        self.excel_page = ExcelPage(context)
        self.history_page = HistoryPage(context)
        self.settings_page = SettingsPage(context)

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.accounts_page)
        self.stack.addWidget(self.preview_page)
        self.stack.addWidget(self.excel_page)
        self.stack.addWidget(self.history_page)
        self.stack.addWidget(self.settings_page)

        layout.addWidget(self.stack, 1)

        # Status bar
        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._status.showMessage("Ready")

        # Wire navigation
        self.navigation.page_changed.connect(self._on_page_changed)

    def _on_page_changed(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
