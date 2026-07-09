from __future__ import annotations

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QAbstractItemView

from app.repositories.history_repository import HistoryRepository


class HistoryPage(QWidget):
    def __init__(self, context) -> None:
        super().__init__()
        self.context = context
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        header = QLabel("History")
        layout.addWidget(header)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Date", "Processed", "Success", "Failed", "Duration (s)"])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table)

        self._load_history()

    def _load_history(self) -> None:
        repo = HistoryRepository()
        entries = repo._session_factory()  # hack: to avoid blocking; ideally query properly
        # For MVP, do nothing — real implementation would query SyncHistory
        pass
