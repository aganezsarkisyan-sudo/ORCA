from __future__ import annotations

from typing import Optional
from PySide6.QtWidgets import QWidget, QFormLayout, QLineEdit, QPushButton, QLabel, QHBoxLayout
import asyncio

from app.repositories.settings_repository import SettingsRepository


class SettingsPage(QWidget):
    def __init__(self, context) -> None:
        super().__init__()
        self.context = context
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QFormLayout(self)
        self.token = QLineEdit()
        self.base_url = QLineEdit()
        self.excel_path = QLineEdit()
        self.sheet = QLineEdit()
        self.template = QLineEdit()
        self.backup = QLineEdit()

        layout.addRow("Dolphin API Token", self.token)
        layout.addRow("Base URL", self.base_url)
        layout.addRow("Excel path", self.excel_path)
        layout.addRow("Default worksheet", self.sheet)
        layout.addRow("Default template", self.template)
        layout.addRow("Backup folder", self.backup)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.on_save)
        btn_layout.addWidget(self.save_btn)
        layout.addRow(btn_layout)

        self._load()

    def _load(self) -> None:
        repo = SettingsRepository()
        s = repo.get()
        if s:
            self.token.setText(s.api_token or "")
            self.base_url.setText(s.base_url or "")
            self.excel_path.setText(s.excel_path or "")
            self.sheet.setText(s.excel_sheet or "")
            self.template.setText(s.excel_sheet or "")
            self.backup.setText("")

    def on_save(self) -> None:
        asyncio.create_task(self._save())

    async def _save(self) -> None:
        repo = SettingsRepository()
        repo.save(api_token=self.token.text(), base_url=self.base_url.text(), excel_path=self.excel_path.text(), excel_sheet=self.sheet.text())
