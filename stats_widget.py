import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout


class StatsWidget(QWidget):
    """Графики телеметрии в реальном времени. Только чтение/отображение."""

    MAX_POINTS = 300

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        pg.setConfigOption("background", "#232427")
        pg.setConfigOption("foreground", "#d4d6d9")

        self.voltage_plot = pg.PlotWidget(title="Напряжение, В")
        self.voltage_plot.showGrid(x=True, y=True, alpha=0.2)
        self.voltage_curve = self.voltage_plot.plot(pen=pg.mkPen("#4fc3f7", width=2))

        self.current_plot = pg.PlotWidget(title="Ток, A")
        self.current_plot.showGrid(x=True, y=True, alpha=0.2)
        self.current_curve = self.current_plot.plot(pen=pg.mkPen("#ff9800", width=2))

        layout.addWidget(self.voltage_plot)
        layout.addWidget(self.current_plot)

        self._v_data = []
        self._c_data = []
        self._x = []
        self._counter = 0

    def add_point(self, voltage: float, current: float = None):
        self._counter += 1
        self._x.append(self._counter)
        self._v_data.append(voltage)
        self._c_data.append(current if current is not None else 0)

        if len(self._x) > self.MAX_POINTS:
            self._x = self._x[-self.MAX_POINTS:]
            self._v_data = self._v_data[-self.MAX_POINTS:]
            self._c_data = self._c_data[-self.MAX_POINTS:]

        self.voltage_curve.setData(self._x, self._v_data)
        self.current_curve.setData(self._x, self._c_data)

    def clear(self):
        self._x.clear()
        self._v_data.clear()
        self._c_data.clear()
        self._counter = 0
        self.voltage_curve.setData([], [])
        self.current_curve.setData([], [])