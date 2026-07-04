from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QProgressBar, QGroupBox
from PyQt6.QtCore import Qt


class MotorsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        group = QGroupBox("Моторы (только отображение, не управление)")
        h = QHBoxLayout(group)

        self.bars = []
        self.labels = []

        for i in range(4):
            col = QVBoxLayout()
            bar = QProgressBar()
            bar.setRange(1000, 2000)
            bar.setValue(1000)
            bar.setFixedWidth(60)
            bar.setMinimumHeight(180)
            bar.setTextVisible(False)
            bar.setStyleSheet("QProgressBar::chunk { background-color: #4caf50; border-radius: 3px; }")

            lbl = QLabel(f"M{i+1}")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            val = QLabel("1000")
            val.setAlignment(Qt.AlignmentFlag.AlignCenter)

            col.addWidget(bar)
            col.addWidget(lbl)
            col.addWidget(val)
            h.addLayout(col)
            self.bars.append(bar)
            self.labels.append(val)

        layout.addWidget(group)
        layout.addStretch()

    def update_motors(self, values):
        for i, v in enumerate(values[:4]):
            self.bars[i].setValue(max(1000, min(2000, v)))
            self.labels[i].setText(str(v))
            pct = (v - 1000) / 1000
            if pct > 0.8:
                color = "#f44336"
            elif pct > 0.5:
                color = "#ff9800"
            else:
                color = "#4caf50"
            self.bars[i].setStyleSheet(
                f"QProgressBar::chunk {{ background-color: {color}; border-radius: 3px; }}"
            )