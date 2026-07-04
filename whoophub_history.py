import os
import csv
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
    QPushButton, QLabel, QFileDialog
)
import pyqtgraph as pg

LOGS_DIR = os.path.join(os.path.dirname(__file__), "data", "logs")


class SessionHistoryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)

        left = QVBoxLayout()
        left.addWidget(QLabel("Сохранённые сессии:"))
        self.session_list = QListWidget()
        self.session_list.itemClicked.connect(self._load_session)
        self.refresh_btn = QPushButton("Обновить список")
        self.refresh_btn.clicked.connect(self._refresh)
        self.open_btn = QPushButton("Открыть CSV...")
        self.open_btn.clicked.connect(self._open_file)
        left.addWidget(self.session_list)
        left.addWidget(self.refresh_btn)
        left.addWidget(self.open_btn)

        right = QVBoxLayout()
        self.info_label = QLabel("Выберите сессию для просмотра")

        pg.setConfigOption("background", "#232427")
        pg.setConfigOption("foreground", "#d4d6d9")

        self.v_plot = pg.PlotWidget(title="Напряжение, В")
        self.v_plot.showGrid(x=True, y=True, alpha=0.2)
        self.v_curve = self.v_plot.plot(pen=pg.mkPen("#4fc3f7", width=2))

        self.c_plot = pg.PlotWidget(title="Ток, A")
        self.c_plot.showGrid(x=True, y=True, alpha=0.2)
        self.c_curve = self.c_plot.plot(pen=pg.mkPen("#ff9800", width=2))

        right.addWidget(self.info_label)
        right.addWidget(self.v_plot)
        right.addWidget(self.c_plot)

        layout.addLayout(left, 1)
        layout.addLayout(right, 2)

        self._refresh()

    def _refresh(self):
        self.session_list.clear()
        os.makedirs(LOGS_DIR, exist_ok=True)
        files = sorted(f for f in os.listdir(LOGS_DIR) if f.endswith(".csv"))
        self.session_list.addItems(files)

    def _load_session(self, item):
        self._plot_csv(os.path.join(LOGS_DIR, item.text()))

    def _open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Открыть CSV", "", "CSV (*.csv)")
        if path:
            self._plot_csv(path)

    def _plot_csv(self, path):
        try:
            times, voltages, currents = [], [], []
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    times.append(i)
                    voltages.append(float(row.get("voltage", 0)))
                    currents.append(float(row.get("current", 0)))
            self.v_curve.setData(times, voltages)
            self.c_curve.setData(times, currents)
            self.info_label.setText(
                f"{os.path.basename(path)} — {len(times)} точек | "
                f"Мин: {min(voltages):.2f}В  Макс: {max(voltages):.2f}В"
            )
        except Exception as e:
            self.info_label.setText(f"Ошибка: {e}")