"""Entry point for ORCA application."""
from __future__ import annotations

import sys
import asyncio
from typing import Final

from qasync import QEventLoop, asyncSlot
from PySide6.QtWidgets import QApplication

from app.ui.main_window import MainWindow
from app.core.app_context import get_app_context
from app.core.logging import setup_logging
from app.core.config import settings

VERSION: Final[str] = "0.1.0"


def _apply_dark_palette(app: QApplication) -> None:
    from PySide6.QtGui import QPalette, QColor

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.Base, QColor(35, 35, 35))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))

    app.setPalette(palette)


def main() -> int:
    setup_logging()

    app = QApplication(sys.argv)
    _apply_dark_palette(app)

    # qasync event loop
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    ctx = get_app_context()

    window = MainWindow(ctx)
    window.show()

    with loop:
        loop.run_forever()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
