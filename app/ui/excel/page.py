from __future__ import annotations

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFileDialog
import asyncio
from pathlib import Path

from app.core.app_context import get_app_context


class ExcelPage(QWidget):
    def __init__(self, context) -> None:
        super().__init__()
        self.context = context
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        header = QLabel("Excel")
        layout.addWidget(header)

        self.path_label = QLabel("No workbook selected")
        layout.addWidget(self.path_label)

        btn_layout = QHBoxLayout()
        self.select_btn = QPushButton("Select workbook")
        self.select_btn.clicked.connect(self.on_select)
        btn_layout.addWidget(self.select_btn)

        self.scan_btn = QPushButton("Scan workbook")
        self.scan_btn.clicked.connect(self.on_scan)
        btn_layout.addWidget(self.scan_btn)

        self.backup_btn = QPushButton("Create backup")
        self.backup_btn.clicked.connect(self.on_backup)
        btn_layout.addWidget(self.backup_btn)

        layout.addLayout(btn_layout)

    def on_select(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select workbook", "", "Excel Files (*.xlsx *.xlsm)")
        if path:
            self.path_label.setText(path)
            # save to settings via repository
            asyncio.create_task(self._save_path(path))

    async def _save_path(self, path: str) -> None:
        # Save to Settings table
        from app.repositories.settings_repository import SettingsRepository
        repo = SettingsRepository()
        repo.save(excel_path=path)

    def on_scan(self) -> None:
        asyncio.create_task(self._scan())

    async def _scan(self) -> None:
        ctx = self.context
        srepo = __import__("app.repositories.settings_repository", fromlist=["SettingsRepository"]).SettingsRepository()
        settings = srepo.get()
        workbook = settings.excel_path if settings else None
        if not workbook:
            self.path_label.setText("No workbook configured")
            return
        # Create report target and scan
        from app.excel.excel_report_target import ExcelReportTarget
        excel_repo = ctx.excel_repo
        matcher = ctx.mapping_service
        excel_mapping_service = ctx.excel_mapping_service
        try:
            ert = ExcelReportTarget(workbook, settings.excel_sheet or "Sheet1", excel_repo, matcher, excel_mapping_service)
            blocks = ert.scan()
            self.path_label.setText(f"Found {len(blocks)} blocks")
        except Exception as exc:
            self.path_label.setText(f"Scan failed: {exc}")

    def on_backup(self) -> None:
        asyncio.create_task(self._backup())

    async def _backup(self) -> None:
        from app.repositories.settings_repository import SettingsRepository
        srepo = SettingsRepository()
        settings = srepo.get()
        if not settings or not settings.excel_path:
            self.path_label.setText("No workbook configured for backup")
            return
        from app.excel.excel_report_target import ExcelReportTarget
        excel_repo = self.context.excel_repo
        matcher = self.context.mapping_service
        excel_mapping_service = self.context.excel_mapping_service
        ert = ExcelReportTarget(settings.excel_path, settings.excel_sheet or "Sheet1", excel_repo, matcher, excel_mapping_service)
        meta = ert.backup()
        self.path_label.setText(f"Backup created: {meta.get('backup_path')}")
