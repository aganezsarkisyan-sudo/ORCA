from __future__ import annotations

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QHBoxLayout
from PySide6.QtCore import Qt
from typing import Any
import asyncio

from app.core.app_context import get_app_context


class DashboardPage(QWidget):
    def __init__(self, context) -> None:
        super().__init__()
        self.context = context
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        header = QLabel("Live Monitor")
        header.setObjectName("Header")
        layout.addWidget(header)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.on_refresh)
        layout.addWidget(self.refresh_btn)

        self.summary = QLabel("Summary: --")
        layout.addWidget(self.summary)

        self.list = QListWidget()
        layout.addWidget(self.list)

    def on_refresh(self) -> None:
        asyncio.create_task(self._refresh())

    async def _refresh(self) -> None:
        ctx = self.context
        # operation id for logs
        ctx.new_operation()
        try:
            summary = await ctx.dolphin_controller.get_dashboard()
            accounts = await ctx.dolphin_controller.get_accounts()
            self.summary.setText(f"Total accounts: {summary.get('total_accounts')}  Total spend: {summary.get('total_spend')}")
            self.list.clear()
            for a in accounts:
                item = QListWidgetItem(f"{a.get('name')} - status: {a.get('status')} - spend: {a.get('spend')}")
                self.list.addItem(item)
        except Exception as exc:
            self.summary.setText("Failed to refresh")
