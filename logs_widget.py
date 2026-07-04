import csv
import os
import time
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLabel

LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "logs")


class LogsWidget(QWidget):
    """Локальные логи телеметрии (только запись/чтение CSV на диске, не влияет на FC)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        os.makedirs(LOGS_DIR, exist_ok=True)

        layout = QVBoxLayout(self)

        top_row = QHBoxLayout()
        self.session_label = QLabel("Сессия не запущена")
        self.start_btn = QPushButton("Начать запись")
        self.stop_btn = QPushButton("Остановить")
        self.stop_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.start_session)
        self.stop_btn.clicked.connect(self.stop_session)
        top_row.addWidget(self.session_label)
        top_row.addStretch()
        top_row.addWidget(self.start_btn)
        top_row.addWidget(self.stop_btn)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Время", "Напряжение, В", "Ток, A", "Расход, мАч"])
        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addLayout(top_row)
        layout.addWidget(self.table)

        self._recording = False
        self._csv_file = None
        self._csv_writer = None

    def start_session(self):
        filename = f"session_{time.strftime('%Y%m%d_%H%M%S')}.csv"
        path = os.path.join(LOGS_DIR, filename)
        self._csv_file = open(path, "w", newline="", encoding="utf-8")
        self._csv_writer = csv.writer(self._csv_file)
        self._csv_writer.writerow(["time", "voltage", "current", "mah"])
        self._recording = True
        self.session_label.setText(f"Запись: {filename}")
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.table.setRowCount(0)

    def stop_session(self):
        self._recording = False
        if self._csv_file:
            self._csv_file.close()
            self._csv_file = None
            self._csv_writer = None
        self.session_label.setText("Сессия остановлена")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def add_entry(self, voltage, current, mah):
        if not self._recording:
            return
        ts = time.strftime("%H:%M:%S")
        self._csv_writer.writerow([ts, voltage, current, mah])
        self._csv_file.flush()

        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(ts))
        self.table.setItem(row, 1, QTableWidgetItem(f"{voltage:.2f}"))
        self.table.setItem(row, 2, QTableWidgetItem(f"{current:.2f}" if current is not None else "-"))
        self.table.setItem(row, 3, QTableWidgetItem(f"{mah:.0f}" if mah is not None else "-"))
        self.table.scrollToBottom()

    def list_sessions(self):
        if not os.path.isdir(LOGS_DIR):
            return []
        return sorted(f for f in os.listdir(LOGS_DIR) if f.endswith(".csv"))