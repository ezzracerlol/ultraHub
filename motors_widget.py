from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QLinearGradient


def small_label(text):
    l = QLabel(text)
    l.setStyleSheet("color:#555;font-size:10px;letter-spacing:2px;background:transparent;border:none;")
    return l


class MotorBar(QWidget):
    def __init__(self, index, parent=None):
        super().__init__(parent)
        self._value = 1000
        self._index = index
        self.setMinimumSize(80, 200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_value(self, v):
        self._value = max(1000, min(2000, v))
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        pct = (self._value - 1000) / 1000

        if pct > 0.8:
            color = QColor("#f44336")
        elif pct > 0.5:
            color = QColor("#ff9800")
        elif pct > 0.1:
            color = QColor("#4caf50")
        else:
            color = QColor("#2a2e3a")

        bar_w = int(w * 0.45)
        bar_x = (w - bar_w) // 2
        bar_h = h - 60
        bar_y = 10

        # Фон полоски
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#1a1e2a"))
        p.drawRoundedRect(bar_x, bar_y, bar_w, bar_h, 4, 4)

        # Заполнение
        fill_h = int(bar_h * pct)
        if fill_h > 0:
            grad = QLinearGradient(0, bar_y + bar_h - fill_h, 0, bar_y + bar_h)
            grad.setColorAt(0, color)
            grad.setColorAt(1, color.darker(150))
            p.setBrush(grad)
            p.drawRoundedRect(bar_x, bar_y + bar_h - fill_h, bar_w, fill_h, 4, 4)

        # Метки процентов
        p.setPen(QColor("#333"))
        p.setFont(QFont("Consolas", 8))
        for mark in [25, 50, 75]:
            y = bar_y + bar_h - int(bar_h * mark / 100)
            p.drawLine(bar_x - 4, y, bar_x, y)
            p.drawLine(bar_x + bar_w, y, bar_x + bar_w + 4, y)

        # Значение
        p.setPen(color)
        p.setFont(QFont("Consolas", 13, QFont.Weight.Bold))
        p.drawText(0, bar_y + bar_h + 18, w, 20, Qt.AlignmentFlag.AlignCenter, str(self._value))

        # Процент
        p.setPen(QColor("#555"))
        p.setFont(QFont("Consolas", 9))
        p.drawText(0, bar_y + bar_h + 34, w, 16, Qt.AlignmentFlag.AlignCenter, f"{int(pct*100)}%")

        # Номер мотора
        p.setPen(QColor("#4fc3f7"))
        p.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        p.drawText(0, bar_y + bar_h + 50, w, 16, Qt.AlignmentFlag.AlignCenter, f"M{self._index+1}")


class MotorsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:#0d0e10;")
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        hdr = QHBoxLayout()
        dot = QLabel("●")
        dot.setStyleSheet("color:#ff9800;font-size:10px;background:transparent;")
        title = QLabel("МОТОРЫ")
        title.setStyleSheet("color:#ff9800;font-size:13px;font-weight:700;letter-spacing:2px;background:transparent;")
        note = QLabel("только отображение газа — не управление")
        note.setStyleSheet("color:#333;font-size:10px;background:transparent;")
        hdr.addWidget(dot)
        hdr.addWidget(title)
        hdr.addWidget(note)
        hdr.addStretch()
        root.addLayout(hdr)

        card = QWidget()
        card.setStyleSheet("background:#111318;border-radius:8px;border:1px solid #1e222a;")
        card_l = QHBoxLayout(card)
        card_l.setContentsMargins(20, 20, 20, 20)
        card_l.setSpacing(16)

        self.motor_bars = []
        for i in range(4):
            bar = MotorBar(i)
            card_l.addWidget(bar)
            self.motor_bars.append(bar)

        root.addWidget(card, 1)

        # Нижняя строка — средний газ
        bottom = QWidget()
        bottom.setStyleSheet("background:#111318;border-radius:8px;border:1px solid #1e222a;")
        bl = QHBoxLayout(bottom)
        bl.setContentsMargins(16, 10, 16, 10)
        self.avg_lbl = QLabel("Средний газ: 1000  |  Макс: 1000  |  Мин: 1000")
        self.avg_lbl.setStyleSheet("color:#555;font-size:11px;background:transparent;")
        bl.addWidget(self.avg_lbl)
        root.addWidget(bottom)

    def update_motors(self, values):
        for i, bar in enumerate(self.motor_bars):
            v = values[i] if i < len(values) else 1000
            bar.set_value(v)
        if values:
            avg = int(sum(values[:4]) / min(4, len(values)))
            mx = max(values[:4])
            mn = min(values[:4])
            self.avg_lbl.setText(f"Средний газ: {avg}  |  Макс: {mx}  |  Мин: {mn}")