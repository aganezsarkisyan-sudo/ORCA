"""Central offsets configuration for Excel templates.

All offsets are (row_offset, col_offset) relative to the anchor cell.
Only offsets.py should be edited when templates change.
"""
from __future__ import annotations

from typing import Tuple

# Offsets are (row_offset, col_offset) where row_offset is added to anchor row
# and col_offset is added to anchor column (both integers).
STATUS: Tuple[int, int] = (-2, 0)
SPEND: Tuple[int, int] = (1, 3)
CPL: Tuple[int, int] = (2, 3)
LEADS_TOTAL: Tuple[int, int] = (3, 3)
LEADS_UNIQUE: Tuple[int, int] = (4, 3)
DEPS: Tuple[int, int] = (5, 3)
AVG_DAYS: Tuple[int, int] = (6, 3)

ALL_OFFSETS = {
    "status": STATUS,
    "spend": SPEND,
    "cpl": CPL,
    "leads_total": LEADS_TOTAL,
    "leads_unique": LEADS_UNIQUE,
    "deps": DEPS,
    "avg_days": AVG_DAYS,
}
