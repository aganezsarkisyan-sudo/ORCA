"""Entry point for ORCA application."""
from __future__ import annotations

from typing import Final
import sys

from PySide6.QtWidgets import QApplication

from app.ui.main_window import MainWindow
from app.core.logging import setup_logging

VERSION: Final[str] = "0.1.0"


def _apply_dark_palette(app: QApplication) -> None:
    """Apply a simple dark palette to the QApplication.

    Kept minimal to avoid extra dependencies.
    """
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
    """Create the QApplication, set up logging and show the main window."""
    setup_logging()
    app = QApplication(sys.argv)
    _apply_dark_palette(app)

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
