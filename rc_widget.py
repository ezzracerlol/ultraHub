from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout
from PyQt6.QtCore import Qt

CHANNEL_NAMES = ["Roll", "Pitch", "Throttle", "Yaw", "AUX1", "AUX2", "AUX3", "AUX4"]
CHANNEL_COLORS = ["#4fc3f7","#4fc3f7","#ff9800","#4fc3f7","#e040fb","#e040fb","#4caf50","#4caf50"]


def small_label(text):
    l = QLabel(text)
    l.setStyleSheet("color:#555;font-size:10px;letter-spacing:2px;background:transparent;border:none;")
    return l


class RCWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:#0d0e10;")
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        hdr = QHBoxLayout()
        dot = QLabel("●")
        dot.setStyleSheet("color:#4fc3f7;font-size:10px;background:transparent;")
        title = QLabel("RC КАНАЛЫ")
        title.setStyleSheet("color:#4fc3f7;font-size:13px;font-weight:700;letter-spacing:2px;background:transparent;")
        note = QLabel("только чтение")
        note.setStyleSheet("color:#333;font-size:10px;background:transparent;")
        hdr.addWidget(dot)
        hdr.addWidget(title)
        hdr.addWidget(note)
        hdr.addStretch()
        root.addLayout(hdr)

        card = QWidget()
        card.setStyleSheet("background:#111318;border-radius:8px;border:1px solid #1e222a;")
        card_l = QVBoxLayout(card)
        card_l.setContentsMargins(16, 14, 16, 14)
        card_l.setSpacing(12)

        self.bars = []
        self.val_labels = []

        for i, (name, color) in enumerate(zip(CHANNEL_NAMES, CHANNEL_COLORS)):
            row = QHBoxLayout()
            row.setSpacing(10)

            name_lbl = QLabel(name)
            name_lbl.setFixedWidth(70)
            name_lbl.setStyleSheet(f"color:#666;font-size:11px;font-weight:600;background:transparent;")

            bar_bg = QWidget()
            bar_bg.setFixedHeight(6)
            bar_bg.setStyleSheet("background:#1a1e2a;border-radius:3px;")

            center_line = QWidget(bar_bg)
            center_line.setGeometry(bar_bg.width()//2, 0, 2, 6)
            center_line.setStyleSheet("background:#2a2e3a;")

            val_lbl = QLabel("1500")
            val_lbl.setFixedWidth(45)
            val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            val_lbl.setStyleSheet(f"color:{color};font-size:12px;font-weight:700;background:transparent;")

            pct_lbl = QLabel("50%")
            pct_lbl.setFixedWidth(35)
            pct_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            pct_lbl.setStyleSheet("color:#444;font-size:10px;background:transparent;")

            row.addWidget(name_lbl)
            row.addWidget(bar_bg, 1)
            row.addWidget(val_lbl)
            row.addWidget(pct_lbl)
            card_l.addLayout(row)
            self.bars.append((bar_bg, color))
            self.val_labels.append((val_lbl, pct_lbl))

        root.addWidget(card)
        root.addStretch()

    def update_channels(self, values):
        for i, ((bar_bg, color), (val_lbl, pct_lbl)) in enumerate(zip(self.bars, self.val_labels)):
            if i >= len(values):
                break
            v = max(1000, min(2000, values[i]))
            pct = int((v - 1000) / 10)
            val_lbl.setText(str(v))
            pct_lbl.setText(f"{pct}%")

            if v < 1100:
                c = "#f44336"
            elif v > 1900:
                c = "#4fc3f7"
            else:
                c = color

            bar_bg.setStyleSheet(
                f"background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                f"stop:0 #1a1e2a,stop:{pct/100} {c},"
                f"stop:{pct/100+0.001} #1a1e2a,stop:1 #1a1e2a);"
                f"border-radius:3px;"
            )