from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QStatusBar
from typing import Final

from app.ui.widgets.navigation import Navigation
from app.ui.dashboard.page import DashboardPage
from app.ui.accounts.page import AccountsPage
from app.ui.settings.page import SettingsPage


class MainWindow(QMainWindow):
    """Main application window.

    Contains a left navigation panel and a stacked widget with pages.
    """

    PAGE_DASHBOARD: Final[int] = 0
    PAGE_ACCOUNTS: Final[int] = 1
    PAGE_SETTINGS: Final[int] = 2

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("ORCA")
        self.resize(1000, 700)

        self._central = QWidget()
        self.setCentralWidget(self._central)

        layout = QHBoxLayout(self._central)
        layout.setContentsMargins(0, 0, 0, 0)

        # Navigation (left)
        self.navigation = Navigation()
        layout.addWidget(self.navigation, 0)

        # Pages (right)
        self.stack = QStackedWidget()
        self.stack.addWidget(DashboardPage())
        self.stack.addWidget(AccountsPage())
        self.stack.addWidget(SettingsPage())
        layout.addWidget(self.stack, 1)

        # Status bar
        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._status.showMessage("Ready")

        # Wire navigation
        self.navigation.page_changed.connect(self._on_page_changed)

    def _on_page_changed(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
