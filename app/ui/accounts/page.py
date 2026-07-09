from __future__ import annotations

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class AccountsPage(QWidget):
    """A placeholder accounts page."""

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("Accounts")
        layout.addWidget(label)
