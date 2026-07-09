"""Safe writer for Excel that writes only changed values, preserves formatting and formulas.

Validations:
- workbook path exists
- worksheet exists
- anchor exists
- target cells exist (basic check)

Behavior:
- Create backup before writing
- Skip cells that contain formulas or are part of merged ranges
- Only write cells whose new_value differs from existing value
- Preserve styles and other properties
"""
from __future__ import annotations

from typing import Iterable, List
from pathlib import Path
from loguru import logger
from openpyxl.utils import coordinate_to_tuple, get_column_letter

from app.excel.workbook import WorkbookHandler, ExcelBlock
from app.excel.preview import PreviewItem


class WorkbookValidationError(Exception):
    pass


class ExcelWriter:
    def __init__(self, workbook: WorkbookHandler) -> None:
        self.workbook = workbook

    def validate(self, preview_items: Iterable[PreviewItem]) -> None:
        if not self.workbook.path.exists():
            raise WorkbookValidationError("Workbook file does not exist")
        if self.workbook.ws is None:
            raise WorkbookValidationError("Worksheet not opened")
        # Ensure anchor cells exist for involved items
        for item in preview_items:
            try:
                _ = self.workbook.get_cell(item.cell)
            except Exception as exc:
                raise WorkbookValidationError(f"Cell {item.cell} not accessible: {exc}")

    def write(self, preview_items: Iterable[PreviewItem]) -> List[str]:
        # Create backup and write changed values. Return list of written cells
        items = list(preview_items)
        if not items:
            logger.info("No changes to write")
            return []

        self.validate(items)
        written: List[str] = []

        # Create backup
        self.workbook._create_backup()

        ws = self.workbook.ws
        for item in items:
            cell = ws[item.cell]
            # Skip merged cells
            in_merged = False
            for merged in ws.merged_cells.ranges:
                if item.cell in merged:
                    in_merged = True
                    break
            if in_merged:
                logger.warning("Skipping merged cell {cell}", cell=item.cell)
                continue

            # Skip formulas
            if isinstance(cell.value, str) and cell.value.startswith("="):
                logger.warning("Skipping formula cell {cell}", cell=item.cell)
                continue

            # Only write if different
            if cell.value != item.new_value:
                # Preserve style by only assigning value; openpyxl retains style unless changed
                cell.value = item.new_value
                written.append(item.cell)
                logger.info("Wrote cell {cell}: {old} -> {new}", cell=item.cell, old=item.old_value, new=item.new_value)
            else:
                logger.debug("No change for cell {cell}", cell=item.cell)

        # Save workbook (the handler will also create another backup if requested)
        self.workbook.save(backup=False)
        logger.info("Workbook saved after writing {n} cells", n=len(written))
        return written
