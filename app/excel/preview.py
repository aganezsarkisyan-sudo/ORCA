"""Preview generator for Excel writes.

Generates a list of changes that would be written to workbook. Each preview
item contains account identifier, field, old value, new value and target cell.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Iterable
from loguru import logger

from app.excel.workbook import WorkbookHandler, ExcelBlock
from app.excel.offsets import ALL_OFFSETS


@dataclass(slots=True)
class PreviewItem:
    account_id: int | None
    account_name: str | None
    field: str
    old_value: Any
    new_value: Any
    cell: str


class PreviewGenerator:
    def __init__(self, workbook: WorkbookHandler) -> None:
        self.workbook = workbook

    def _calc_cell(self, anchor: str, offset: tuple[int, int]) -> str:
        row, col = WorkbookHandler.coord_to_tuple(anchor)
        target_row = row + offset[0]
        target_col = col + offset[1]
        return WorkbookHandler.tuple_to_coord(target_row, target_col)

    def generate(self, blocks: Iterable[ExcelBlock], account_values: Iterable[tuple[int, str, dict]]) -> List[PreviewItem]:
        """account_values: iterable of (account_id, account_name, values_dict)

        values_dict keys should match ALL_OFFSETS keys.
        """
        # Build a mapping from block name to anchor
        anchor_map = {b.name: b.anchor_cell for b in blocks}
        items: List[PreviewItem] = []

        for account_id, account_name, values in account_values:
            # Expect that account_name corresponds to block name; if not, try key existence
            if account_name not in anchor_map:
                # skip if no corresponding block
                continue
            anchor = anchor_map[account_name]
            for field, offset in ALL_OFFSETS.items():
                cell = self._calc_cell(anchor, offset)
                try:
                    old = self.workbook.get_cell_value(cell)
                except Exception:
                    old = None
                new = values.get(field)
                if new is None:
                    continue
                if old != new:
                    item = PreviewItem(account_id=account_id, account_name=account_name, field=field, old_value=old, new_value=new, cell=cell)
                    items.append(item)
                    logger.debug("Preview change: {item}", item=item)
        logger.info("Generated preview with {n} items", n=len(items))
        return items
