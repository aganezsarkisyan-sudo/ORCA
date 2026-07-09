"""Scanner to discover Excel blocks (account anchors) in a worksheet.

Heuristics:
- A block title is a short alphanumeric token with letters and digits (e.g., NBA44).
- We scan all cells and consider non-empty strings matching pattern as block titles.
- Anchor cell is the cell coordinate where the title was found.

Returns list of ExcelBlock instances.
"""
from __future__ import annotations

import re
from typing import Iterable, List
from loguru import logger

from app.excel.workbook import WorkbookHandler, ExcelBlock

TITLE_RE = re.compile(r"^[A-Z0-9\-_]{2,}$")


class Scanner:
    def __init__(self, workbook: WorkbookHandler) -> None:
        self.workbook = workbook

    def scan_blocks(self) -> List[ExcelBlock]:
        if self.workbook.ws is None:
            raise RuntimeError("Workbook not opened")

        blocks: List[ExcelBlock] = []
        ws = self.workbook.ws
        logger.info("Scanning worksheet for blocks")

        for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
            for cell in row:
                val = cell.value
                if not isinstance(val, str):
                    continue
                text = val.strip()
                if not text:
                    continue
                # Heuristic: uppercase token with letters/digits and optional -_
                if TITLE_RE.match(text):
                    coord = cell.coordinate
                    block = ExcelBlock(name=text, anchor_cell=coord, row=cell.row, column=cell.column)
                    blocks.append(block)
                    logger.debug("Found block {name} at {coord}", name=text, coord=coord)
        logger.info("Found {n} blocks", n=len(blocks))
        return blocks
