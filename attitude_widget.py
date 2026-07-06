import math
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QRegion, QLinearGradient


def small_label(text):
    l = QLabel(text)
    l.setStyleSheet("color:#555;font-size:10px;letter-spacing:2px;background:transparent;border:none;")
    return l


class HorizonDisplay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 300)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._roll = 0.0
        self._pitch = 0.0

    def set_attitude(self, roll, pitch):
        self._roll = roll
        self._pitch = pitch
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        r = min(w, h) / 2 - 10

        # Обрезаем по кругу
        clip = QRegion(int(cx - r), int(cy - r), int(2*r), int(2*r), QRegion.RegionType.Ellipse)
        p.setClipRegion(clip)

        p.save()
        p.translate(cx, cy)
        p.rotate(-self._roll)
        pitch_offset = self._pitch / 90.0 * r

        # Небо — градиент
        sky_grad = QLinearGradient(0, -r - pitch_offset - 1, 0, -pitch_offset)
        sky_grad.setColorAt(0, QColor("#0a1628"))
        sky_grad.setColorAt(1, QColor("#1a4a7a"))
        p.fillRect(int(-r), int(-r - pitch_offset) - 1, int(2*r) + 2, int(r + pitch_offset) + 1, sky_grad)

        # Земля — градиент
        gnd_grad = QLinearGradient(0, -pitch_offset, 0, r - pitch_offset)
        gnd_grad.setColorAt(0, QColor("#3a2a0a"))
        gnd_grad.setColorAt(1, QColor("#1a1206"))
        p.fillRect(int(-r), int(-pitch_offset), int(2*r) + 2, int(r) + 2, gnd_grad)

        # Горизонт
        p.setPen(QPen(QColor("white"), 2))
        p.drawLine(int(-r), int(-pitch_offset), int(r), int(-pitch_offset))

        # Метки тангажа
        p.setFont(QFont("Consolas", 8))
        for deg in [-20, -10, 10, 20]:
            y_pos = int(-pitch_offset - deg / 90.0 * r)
            line_w = 30 if deg % 20 == 0 else 20
            p.setPen(QPen(QColor(255, 255, 255, 150), 1))
            p.drawLine(-line_w, y_pos, line_w, y_pos)
            p.setPen(QColor(200, 200, 200))
            p.drawText(line_w + 4, y_pos + 4, f"{deg}°")

        p.restore()
        p.setClipping(False)

        # Обводка
        p.setPen(QPen(QColor("#1e222a"), 3))
        p.drawEllipse(int(cx - r), int(cy - r), int(2*r), int(2*r))

        # Метки крена (по кругу)
        p.setPen(QPen(QColor("#4fc3f7"), 1))
        for deg in [-60, -45, -30, -20, -10, 0, 10, 20, 30, 45, 60]:
            angle = (deg - 90) * math.pi / 180
            x1 = cx + (r - 8) * math.cos(angle)
            y1 = cy + (r - 8) * math.sin(angle)
            x2 = cx + r * math.cos(angle)
            y2 = cy + r * math.sin(angle)
            p.drawLine(int(x1), int(y1), int(x2), int(y2))

        # Указатель крена
        roll_rad = (self._roll - 90) * math.pi / 180
        px1 = cx + (r - 14) * math.cos(roll_rad)
        py1 = cy + (r - 14) * math.sin(roll_rad)
        px2 = cx + (r + 2) * math.cos(roll_rad)
        py2 = cy + (r + 2) * math.sin(roll_rad)
        p.setPen(QPen(QColor("#ffeb3b"), 2))
        p.drawLine(int(px1), int(py1), int(px2), int(py2))

        # Центральный прицел
        p.setPen(QPen(QColor("#ffeb3b"), 2))
        p.drawLine(int(cx) - 40, int(cy), int(cx) - 10, int(cy))
        p.drawLine(int(cx) + 10, int(cy), int(cx) + 40, int(cy))
        p.drawLine(int(cx), int(cy) - 10, int(cx), int(cy) - 30)
        p.drawEllipse(int(cx) - 5, int(cy) - 5, 10, 10)

        p.end()


class AttitudeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:#0d0e10;")
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        hdr = QHBoxLayout()
        dot = QLabel("●")
        dot.setStyleSheet("color:#ffeb3b;font-size:10px;background:transparent;")
        title = QLabel("ГОРИЗОНТ / ATTITUDE")
        title.setStyleSheet("color:#ffeb3b;font-size:13px;font-weight:700;letter-spacing:2px;background:transparent;")
        hdr.addWidget(dot)
        hdr.addWidget(title)
        hdr.addStretch()
        root.addLayout(hdr)

        # Основная область
        main_row = QHBoxLayout()
        main_row.setSpacing(8)

        # Горизонт
        horizon_card = QWidget()
        horizon_card.setStyleSheet("background:#111318;border-radius:8px;border:1px solid #1e222a;")
        hl = QVBoxLayout(horizon_card)
        hl.setContentsMargins(10, 10, 10, 10)
        self.horizon = HorizonDisplay()
        hl.addWidget(self.horizon)

        # Данные
        data_card = QWidget()
        data_card.setFixedWidth(200)
        data_card.setStyleSheet("background:#111318;border-radius:8px;border:1px solid #1e222a;")
        dl = QVBoxLayout(data_card)
        dl.setContentsMargins(16, 14, 16, 14)
        dl.setSpacing(16)

        dl.addWidget(small_label("ДАННЫЕ"))

        self.data_widgets = {}
        for label, key, color in [
            ("ROLL", "roll", "#4fc3f7"),
            ("PITCH", "pitch", "#ff9800"),
            ("YAW", "yaw", "#e040fb"),
        ]:
            col = QVBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet(f"color:#555;font-size:10px;letter-spacing:2px;background:transparent;")
            val = QLabel("0.0°")
            val.setStyleSheet(f"color:{color};font-size:26px;font-weight:700;background:transparent;")
            col.addWidget(lbl)
            col.addWidget(val)
            dl.addLayout(col)
            self.data_widgets[key] = val

        dl.addStretch()

        main_row.addWidget(horizon_card, 1)
        main_row.addWidget(data_card)
        root.addLayout(main_row, 1)

    def update_attitude(self, roll, pitch, yaw):
        self.horizon.set_attitude(roll, pitch)
        self.data_widgets["roll"].setText(f"{roll:.1f}°")
        self.data_widgets["pitch"].setText(f"{pitch:.1f}°")
        self.data_widgets["yaw"].setText(f"{yaw:.0f}°")