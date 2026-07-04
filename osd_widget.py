from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QFont, QPen


class OSDOverlay(QWidget):
    """Симулятор OSD — отображает телеметрию поверх чёрного фона как на реальном FPV экране."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(640, 480)
        self.setStyleSheet("background-color: #0a0a0a;")

        self._voltage  = 0.0
        self._current  = 0.0
        self._mah      = 0
        self._rssi     = 0
        self._roll     = 0.0
        self._pitch    = 0.0
        self._yaw      = 0.0
        self._armed    = False
        self._sats     = 0
        self._flight_time = 0

        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)

    def _tick(self):
        if self._armed:
            self._flight_time += 1
        self.update()

    def update_telemetry(self, voltage=None, current=None, mah=None,
                         rssi=None, roll=None, pitch=None, yaw=None,
                         armed=None, sats=None):
        if voltage  is not None: self._voltage  = voltage
        if current  is not None: self._current  = current
        if mah      is not None: self._mah      = mah
        if rssi     is not None: self._rssi     = rssi
        if roll     is not None: self._roll     = roll
        if pitch    is not None: self._pitch    = pitch
        if yaw      is not None: self._yaw      = yaw
        if armed    is not None:
            if armed and not self._armed:
                self._flight_time = 0
            self._armed = armed
        if sats     is not None: self._sats     = sats
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # Фон — имитация FPV картинки (тёмно-серый)
        p.fillRect(0, 0, w, h, QColor(15, 15, 20))

        # Сетка (имитация слабого видеосигнала)
        p.setPen(QPen(QColor(30, 32, 38), 1))
        for x in range(0, w, 40):
            p.drawLine(x, 0, x, h)
        for y in range(0, h, 40):
            p.drawLine(0, y, w, y)

        osd = QFont("Consolas", 14, QFont.Weight.Bold)
        osd_small = QFont("Consolas", 11, QFont.Weight.Bold)
        p.setFont(osd)

        def draw_text(x, y, text, color=QColor(255,255,255), shadow=True):
            if shadow:
                p.setPen(QColor(0,0,0,200))
                p.drawText(x+2, y+2, text)
            p.setPen(color)
            p.drawText(x, y, text)

        # === ВЕРХНИЙ ЛЕВЫЙ — ARMED/DISARMED ===
        if self._armed:
            draw_text(20, 35, "ARMED", QColor(255, 80, 80))
        else:
            draw_text(20, 35, "DISARMED", QColor(150, 150, 150))

        # === ВЕРХНИЙ ПРАВЫЙ — RSSI ===
        rssi_color = QColor(80,255,80) if self._rssi > 50 else QColor(255,150,0) if self._rssi > 25 else QColor(255,50,50)
        draw_text(w-160, 35, f"RSSI {self._rssi}%", rssi_color)

        # === НИЖНИЙ ЛЕВЫЙ — БАТАРЕЯ ===
        volt_color = QColor(80,255,80)
        if self._voltage < 3.5:
            volt_color = QColor(255, 50, 50)
        elif self._voltage < 3.7:
            volt_color = QColor(255, 180, 0)

        draw_text(20, h-90, f"{self._voltage:.2f}V", volt_color)
        p.setFont(osd_small)
        draw_text(20, h-68, f"{self._current:.1f}A", QColor(200,200,200))
        draw_text(20, h-48, f"{int(self._mah)}mAh", QColor(180,180,180))
        p.setFont(osd)

        # Полоска заряда
        bar_x, bar_y, bar_w, bar_h = 20, h-35, 120, 12
        p.fillRect(bar_x, bar_y, bar_w, bar_h, QColor(40,40,40))
        fill = int(bar_w * max(0, min(1, (self._voltage - 3.0) / 1.35)))
        fc = QColor(80,255,80) if fill > bar_w*0.5 else QColor(255,180,0) if fill > bar_w*0.25 else QColor(255,50,50)
        p.fillRect(bar_x, bar_y, fill, bar_h, fc)
        p.setPen(QColor(100,100,100))
        p.drawRect(bar_x, bar_y, bar_w, bar_h)

        # === НИЖНИЙ ПРАВЫЙ — ВРЕМЯ ПОЛЁТА ===
        mins = self._flight_time // 60
        secs = self._flight_time % 60
        draw_text(w-140, h-48, f"{mins:02d}:{secs:02d}", QColor(200,200,255))

        # GPS
        if self._sats > 0:
            gps_c = QColor(80,255,80) if self._sats >= 6 else QColor(255,180,0)
            p.setFont(osd_small)
            draw_text(w-140, h-28, f"GPS {self._sats} sats", gps_c)
            p.setFont(osd)

        # === ЦЕНТР — КРОССХЕЙР ===
        cx, cy = w//2, h//2
        p.setPen(QPen(QColor(255,255,255,200), 2))
        p.drawLine(cx-30, cy, cx-8, cy)
        p.drawLine(cx+8,  cy, cx+30, cy)
        p.drawLine(cx, cy-30, cx, cy-8)
        p.drawLine(cx, cy+8,  cx, cy+30)
        p.drawEllipse(cx-4, cy-4, 8, 8)

        # Горизонт
        import math
        roll_rad = self._roll * math.pi / 180
        hlen = 60
        hx1 = cx - int(hlen * math.cos(roll_rad))
        hy1 = cy - int(hlen * math.sin(roll_rad))
        hx2 = cx + int(hlen * math.cos(roll_rad))
        hy2 = cy + int(hlen * math.sin(roll_rad))
        p.setPen(QPen(QColor(255, 200, 0, 180), 2))
        p.drawLine(hx1, hy1, hx2, hy2)

        # Pitch
        p.setFont(osd_small)
        draw_text(cx+50, cy+5, f"P {self._pitch:.1f}", QColor(200,220,255))
        draw_text(cx+50, cy+20, f"R {self._roll:.1f}",  QColor(200,220,255))
        draw_text(cx+50, cy+35, f"Y {self._yaw:.0f}",   QColor(200,220,255))

        # === НАЗВАНИЕ ДРОНА ===
        p.setFont(QFont("Consolas", 10))
        draw_text(cx-80, 35, "BetaFPV Air75 II", QColor(180,180,180))

        p.end()


class OSDWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        info = QLabel("OSD симулятор — отображает телеметрию как на реальном FPV экране (данные берутся при подключении дрона)")
        info.setStyleSheet("color: #7a7d81; font-size: 11px;")
        info.setWordWrap(True)
        layout.addWidget(info)

        self.osd = OSDOverlay()
        layout.addWidget(self.osd)

    def update_telemetry(self, **kwargs):
        self.osd.update_telemetry(**kwargs)