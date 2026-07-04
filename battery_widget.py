from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QGroupBox
from PyQt6.QtCore import Qt


class BatteryWidget(QGroupBox):
    """Только отображение телеметрии АКБ — без записи каких-либо настроек в FC."""

    def __init__(self, full_v=4.35, empty_v=3.0, warn_v=3.3, parent=None):
        super().__init__("Аккумулятор", parent)
        self.full_v = full_v
        self.empty_v = empty_v
        self.warn_v = warn_v

        layout = QVBoxLayout(self)

        self.voltage_label = QLabel("-- В")
        self.voltage_label.setObjectName("valueLabel")
        self.voltage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.bar.setTextVisible(True)

        info_row = QHBoxLayout()
        self.current_label = QLabel("Ток: -- A")
        self.mah_label = QLabel("Расход: -- мАч")
        info_row.addWidget(self.current_label)
        info_row.addWidget(self.mah_label)

        layout.addWidget(self.voltage_label)
        layout.addWidget(self.bar)
        layout.addLayout(info_row)

    def update_values(self, voltage: float, current: float = None, mah: float = None):
        self.voltage_label.setText(f"{voltage:.2f} В")

        pct = (voltage - self.empty_v) / (self.full_v - self.empty_v) * 100
        pct = max(0, min(100, pct))
        self.bar.setValue(int(pct))

        if voltage <= self.warn_v:
            color = "#f44336"
        elif pct < 40:
            color = "#ff9800"
        else:
            color = "#4caf50"
        self.bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {color}; border-radius: 3px; }}")

        if current is not None:
            self.current_label.setText(f"Ток: {current:.2f} A")
        if mah is not None:
            self.mah_label.setText(f"Расход: {mah:.0f} мАч")

    def reset(self):
        self.voltage_label.setText("-- В")
        self.bar.setValue(0)
        self.current_label.setText("Ток: -- A")
        self.mah_label.setText("Расход: -- мАч")