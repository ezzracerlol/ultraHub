import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt


def small_label(text):
    l = QLabel(text)
    l.setStyleSheet("color:#555;font-size:10px;letter-spacing:2px;background:transparent;border:none;")
    return l


class StatsWidget(QWidget):
    MAX_POINTS = 300

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:#0d0e10;")
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        hdr = QHBoxLayout()
        dot = QLabel("●")
        dot.setStyleSheet("color:#4caf50;font-size:10px;background:transparent;")
        title = QLabel("СТАТИСТИКА")
        title.setStyleSheet("color:#4caf50;font-size:13px;font-weight:700;letter-spacing:2px;background:transparent;")
        hdr.addWidget(dot)
        hdr.addWidget(title)
        hdr.addStretch()

        # Мини статы
        self.min_v = QLabel("Мин В: --")
        self.max_v = QLabel("Макс В: --")
        self.avg_v = QLabel("Ср В: --")
        for lbl in [self.min_v, self.max_v, self.avg_v]:
            lbl.setStyleSheet("color:#555;font-size:11px;background:transparent;margin-left:12px;")
            hdr.addWidget(lbl)

        root.addLayout(hdr)

        pg.setConfigOption("background", "#111318")
        pg.setConfigOption("foreground", "#d4d6d9")

        # График напряжения
        v_card = QWidget()
        v_card.setStyleSheet("background:#111318;border-radius:8px;border:1px solid #1e222a;")
        vl = QVBoxLayout(v_card)
        vl.setContentsMargins(12, 10, 12, 10)
        vl.addWidget(small_label("НАПРЯЖЕНИЕ, В"))
        self.v_plot = pg.PlotWidget()
        self.v_plot.setBackground("#111318")
        self.v_plot.showGrid(x=True, y=True, alpha=0.1)
        self.v_plot.getAxis("left").setTextPen("#555")
        self.v_plot.getAxis("bottom").setTextPen("#555")
        self.v_curve = self.v_plot.plot(pen=pg.mkPen("#4fc3f7", width=2))
        self.v_fill = pg.FillBetweenItem(
            self.v_curve,
            self.v_plot.plot([0], [0]),
            brush=pg.mkBrush(79, 195, 247, 30)
        )
        self.v_plot.addItem(self.v_fill)
        vl.addWidget(self.v_plot)

        # График тока
        c_card = QWidget()
        c_card.setStyleSheet("background:#111318;border-radius:8px;border:1px solid #1e222a;")
        cl = QVBoxLayout(c_card)
        cl.setContentsMargins(12, 10, 12, 10)
        cl.addWidget(small_label("ТОК, А"))
        self.c_plot = pg.PlotWidget()
        self.c_plot.setBackground("#111318")
        self.c_plot.showGrid(x=True, y=True, alpha=0.1)
        self.c_plot.getAxis("left").setTextPen("#555")
        self.c_plot.getAxis("bottom").setTextPen("#555")
        self.c_curve = self.c_plot.plot(pen=pg.mkPen("#ff9800", width=2))
        cl.addWidget(self.c_plot)

        root.addWidget(v_card, 1)
        root.addWidget(c_card, 1)

        self._v_data = []
        self._c_data = []
        self._x = []
        self._counter = 0

    def add_point(self, voltage, current=None):
        self._counter += 1
        self._x.append(self._counter)
        self._v_data.append(voltage)
        self._c_data.append(current if current is not None else 0)

        if len(self._x) > self.MAX_POINTS:
            self._x = self._x[-self.MAX_POINTS:]
            self._v_data = self._v_data[-self.MAX_POINTS:]
            self._c_data = self._c_data[-self.MAX_POINTS:]

        self.v_curve.setData(self._x, self._v_data)
        self.c_curve.setData(self._x, self._c_data)

        if self._v_data:
            self.min_v.setText(f"Мин В: {min(self._v_data):.2f}")
            self.max_v.setText(f"Макс В: {max(self._v_data):.2f}")
            self.avg_v.setText(f"Ср В: {sum(self._v_data)/len(self._v_data):.2f}")

    def clear(self):
        self._x.clear()
        self._v_data.clear()
        self._c_data.clear()
        self._counter = 0
        self.v_curve.setData([], [])
        self.c_curve.setData([], [])