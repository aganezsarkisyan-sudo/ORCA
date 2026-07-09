from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List
from loguru import logger

from app.excel.workbook import WorkbookHandler
from app.excel.scanner import Scanner
from app.excel.preview import PreviewGenerator, PreviewItem
from app.excel.writer import ExcelWriter
from app.repositories.excel_mapping_repository import ExcelMappingRepository
from app.services.excel_mapping_service import ExcelMappingService
from app.services.mapping_service import MappingService


@dataclass
class ValidationErrorItem:
    code: str
    message: str
    field: str | None = None


class ReportTarget:
    """Abstract report target interface."""

    def scan(self, workbook_path: str, worksheet: str) -> list:
        raise NotImplementedError

    def preview(self, template_name: str) -> list[PreviewItem]:
        raise NotImplementedError

    def write(self, preview_items: Iterable[PreviewItem], dry_run: bool = False) -> list[str]:
        raise NotImplementedError

    def validate(self) -> list[ValidationErrorItem]:
        raise NotImplementedError

    def backup(self) -> dict:
        raise NotImplementedError


class ExcelReportTarget(ReportTarget):
    def __init__(self, workbook_path: str, worksheet: str, excel_repo: ExcelMappingRepository, mapping_service: MappingService, excel_mapping_service: ExcelMappingService) -> None:
        self.workbook_path = workbook_path
        self.worksheet = worksheet
        self.excel_repo = excel_repo
        self.mapping_service = mapping_service
        self.excel_mapping_service = excel_mapping_service

        self.wb_handler = WorkbookHandler(workbook_path)
        self.wb_handler.open(worksheet)
        self.scanner = Scanner(self.wb_handler)
        self.preview_gen = PreviewGenerator(self.wb_handler)
        self.writer = ExcelWriter(self.wb_handler)

    def scan(self) -> list:
        blocks = self.scanner.scan_blocks()
        # return list of ExcelBlock
        return blocks

    def preview(self, template_name: str, account_values: Iterable[tuple[int, str, dict]]) -> List[PreviewItem]:
        # account_values: (account_id, block_name, values)
        return self.preview_gen.generate(self.scan(), account_values)

    def write(self, preview_items: Iterable[PreviewItem], dry_run: bool = False) -> list[str]:
        if dry_run:
            # validate but don't write
            try:
                self.writer.validate(preview_items)
            except Exception:
                pass
            # Return the list of would-be written cells
            return [p.cell for p in preview_items if p.new_value != p.old_value]
        # perform actual write
        written = self.writer.write(preview_items)
        return written

    def validate(self) -> List[ValidationErrorItem]:
        errors: List[ValidationErrorItem] = []
        # basic validations
        try:
            # workbook opened in constructor; if missing will raise earlier
            if self.wb_handler.ws is None:
                errors.append(ValidationErrorItem(code="worksheet_missing", message="Worksheet not opened"))
        except FileNotFoundError as exc:
            errors.append(ValidationErrorItem(code="workbook_missing", message=str(exc)))
        return errors

    def backup(self) -> dict:
        # create backup and record checksum + metadata
        bak = self.wb_handler._create_backup()
        checksum = hashlib.sha256(Path(self.workbook_path).read_bytes()).hexdigest()
        meta = {"backup_path": str(bak), "checksum": checksum, "timestamp": datetime.utcnow().isoformat()}
        # write metadata next to backup
        meta_path = Path(str(bak) + ".meta.json")
        meta_path.write_text(json.dumps(meta))
        logger.info("Created backup with metadata {meta}", meta=meta)
        return meta
