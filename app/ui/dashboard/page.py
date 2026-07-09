from __future__ import annotations

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class DashboardPage(QWidget):
    """A placeholder dashboard page."""

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("Dashboard")
        label.setObjectName("DashboardLabel")
        layout.addWidget(label)
