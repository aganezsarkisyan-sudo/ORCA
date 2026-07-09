from __future__ import annotations

from typing import Any
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLabel,
    QAbstractItemView,
)
import asyncio

from app.core.app_context import get_app_context


class AccountsPage(QWidget):
    def __init__(self, context) -> None:
        super().__init__()
        self.context = context
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        header = QLabel("Accounts")
        layout.addWidget(header)

        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.on_refresh)
        btn_layout.addWidget(self.refresh_btn)

        self.auto_match_btn = QPushButton("Auto Match")
        self.auto_match_btn.clicked.connect(self.on_auto_match)
        btn_layout.addWidget(self.auto_match_btn)

        layout.addLayout(btn_layout)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["Dolphin name", "Local name", "Status", "Template", "Worksheet", "Anchor", "Confidence"])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table)

    def on_refresh(self) -> None:
        asyncio.create_task(self._refresh())

    async def _refresh(self) -> None:
        ctx = self.context
        accounts = await ctx.dolphin_controller.get_accounts()
        self.table.setRowCount(0)
        for a in accounts:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(a.get("name") or ""))
            self.table.setItem(row, 1, QTableWidgetItem(a.get("name") or ""))
            self.table.setItem(row, 2, QTableWidgetItem(a.get("status") or ""))
            # place holders for mapping details
            self.table.setItem(row, 3, QTableWidgetItem(""))
            self.table.setItem(row, 4, QTableWidgetItem(""))
            self.table.setItem(row, 5, QTableWidgetItem(""))
            self.table.setItem(row, 6, QTableWidgetItem(""))

    def on_auto_match(self) -> None:
        # trigger mapping flow (scanner+mapper) — simplified: just refresh
        asyncio.create_task(self._auto_match())

    async def _auto_match(self) -> None:
        # For MVP, just call refresh; detailed mapping is a separate flow
        await self._refresh()
