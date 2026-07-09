from __future__ import annotations

from typing import Iterable
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView, QHBoxLayout
import asyncio

from app.core.app_context import get_app_context
from app.excel.preview import PreviewItem


class PreviewPage(QWidget):
    def __init__(self, context) -> None:
        super().__init__()
        self.context = context
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        header = QLabel("Preview")
        layout.addWidget(header)

        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh Preview")
        self.refresh_btn.clicked.connect(self.on_refresh)
        btn_layout.addWidget(self.refresh_btn)

        self.write_btn = QPushButton("Write to Excel")
        self.write_btn.clicked.connect(self.on_write)
        btn_layout.addWidget(self.write_btn)

        layout.addLayout(btn_layout)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Account", "Field", "Old value", "New value", "Cell", "Status"])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table)

    def on_refresh(self) -> None:
        asyncio.create_task(self._refresh())

    async def _refresh(self) -> None:
        ctx = self.context
        # For now, build a simple preview using scanner/mapping on default workbook/settings
        settings = ctx.account_repo  # placeholder
        # This should call ExcelReportTarget.preview in full implementation
        # We'll display empty preview for now
        self.table.setRowCount(0)

    def on_write(self) -> None:
        asyncio.create_task(self._write())

    async def _write(self) -> None:
        # For MVP, show placeholder
        pass
