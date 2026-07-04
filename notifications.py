from PyQt6.QtWidgets import QSystemTrayIcon, QApplication
from PyQt6.QtCore import QObject


class WhoopNotifier(QObject):
    def __init__(self):
        super().__init__()
        self._tray = None
        self._last_warn = False

    def setup(self, tray_icon: QSystemTrayIcon):
        self._tray = tray_icon

    def check_voltage(self, voltage: float, warn_v: float, empty_v: float):
        if voltage <= empty_v:
            self._notify("⚠️ БАТАРЕЯ РАЗРЯЖЕНА!", f"{voltage:.2f}В — срочно садись!", critical=True)
        elif voltage <= warn_v and not self._last_warn:
            self._notify("🔋 Низкий заряд", f"Напряжение: {voltage:.2f}В")
            self._last_warn = True
        elif voltage > warn_v + 0.1:
            self._last_warn = False

    def _notify(self, title, msg, critical=False):
        if self._tray:
            icon = QSystemTrayIcon.MessageIcon.Critical if critical else QSystemTrayIcon.MessageIcon.Warning
            self._tray.showMessage(title, msg, icon, 3000)