from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QProgressBar, QGroupBox

CHANNEL_NAMES = ["Roll", "Pitch", "Throttle", "Yaw", "AUX1", "AUX2", "AUX3", "AUX4"]


class RCWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        group = QGroupBox("RC Каналы (только чтение)")
        grid = QGridLayout(group)

        self.bars = []
        self.labels = []

        for i, name in enumerate(CHANNEL_NAMES):
            lbl = QLabel(name)
            bar = QProgressBar()
            bar.setRange(1000, 2000)
            bar.setValue(1500)
            bar.setFormat("%v")
            val_lbl = QLabel("1500")
            val_lbl.setFixedWidth(45)
            grid.addWidget(lbl, i, 0)
            grid.addWidget(bar, i, 1)
            grid.addWidget(val_lbl, i, 2)
            self.bars.append(bar)
            self.labels.append(val_lbl)

        layout.addWidget(group)
        layout.addStretch()

    def update_channels(self, values):
        for i, v in enumerate(values[:len(self.bars)]):
            self.bars[i].setValue(max(1000, min(2000, v)))
            self.labels[i].setText(str(v))
            if v < 1100:
                color = "#f44336"
            elif v > 1900:
                color = "#4fc3f7"
            else:
                color = "#4caf50"
            self.bars[i].setStyleSheet(
                f"QProgressBar::chunk {{ background-color: {color}; border-radius: 3px; }}"
            )