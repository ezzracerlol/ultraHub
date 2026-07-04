from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QRegion


class HorizonDisplay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(220, 220)
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
        r = min(w, h) / 2 - 5

        clip = QRegion(int(cx - r), int(cy - r), int(2 * r), int(2 * r), QRegion.RegionType.Ellipse)
        p.setClipRegion(clip)

        p.save()
        p.translate(cx, cy)
        p.rotate(-self._roll)
        pitch_offset = self._pitch / 90.0 * r

        p.fillRect(int(-r), int(-r - pitch_offset) - 1, int(2 * r) + 2, int(r + pitch_offset) + 1, QColor("#1a6494"))
        p.fillRect(int(-r), int(-pitch_offset), int(2 * r) + 2, int(r) + 2, QColor("#7a5c2e"))

        p.setPen(QPen(QColor("white"), 2))
        p.drawLine(int(-r), int(-pitch_offset), int(r), int(-pitch_offset))
        p.restore()

        p.setClipping(False)
        p.setPen(QPen(QColor("yellow"), 2))
        p.drawEllipse(int(cx) - 4, int(cy) - 4, 8, 8)
        p.drawLine(int(cx) - 22, int(cy), int(cx) - 6, int(cy))
        p.drawLine(int(cx) + 6, int(cy), int(cx) + 22, int(cy))

        p.setPen(QPen(QColor("#45484d"), 2))
        p.drawEllipse(int(cx - r), int(cy - r), int(2 * r), int(2 * r))


class AttitudeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.horizon = HorizonDisplay()
        layout.addWidget(self.horizon, alignment=Qt.AlignmentFlag.AlignCenter)

        info = QHBoxLayout()
        self.roll_lbl = QLabel("Roll: 0.0°")
        self.pitch_lbl = QLabel("Pitch: 0.0°")
        self.yaw_lbl = QLabel("Yaw: 0.0°")
        for l in [self.roll_lbl, self.pitch_lbl, self.yaw_lbl]:
            l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            info.addWidget(l)
        layout.addLayout(info)
        layout.addStretch()

    def update_attitude(self, roll, pitch, yaw):
        self.horizon.set_attitude(roll, pitch)
        self.roll_lbl.setText(f"Roll: {roll:.1f}°")
        self.pitch_lbl.setText(f"Pitch: {pitch:.1f}°")
        self.yaw_lbl.setText(f"Yaw: {yaw:.1f}°")