from __future__ import annotations

from typing import Callable
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem
from PySide6.QtCore import Signal


class Navigation(QWidget):
    """Simple left navigation implemented with a QListWidget.

    Emits page_changed(index: int) when the selection changes.
    """

    page_changed: Signal = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("Navigation")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        self.list = QListWidget()
        self.list.addItem(QListWidgetItem("Dashboard"))
        self.list.addItem(QListWidgetItem("Accounts"))
        self.list.addItem(QListWidgetItem("Settings"))
        self.list.setCurrentRow(0)
        self.list.currentRowChanged.connect(self.page_changed.emit)

        layout.addWidget(self.list)
