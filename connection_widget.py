from PyQt6.QtWidgets import QGroupBox, QHBoxLayout, QComboBox, QPushButton, QLabel
from PyQt6.QtCore import pyqtSignal


class ConnectionWidget(QGroupBox):
    connect_requested = pyqtSignal(str)
    disconnect_requested = pyqtSignal()
    refresh_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("Подключение", parent)
        layout = QHBoxLayout(self)

        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(150)

        self.refresh_btn = QPushButton("Обновить")
        self.refresh_btn.clicked.connect(self.refresh_requested.emit)

        self.connect_btn = QPushButton("Подключить")
        self.connect_btn.clicked.connect(self._on_connect_click)

        self.status_label = QLabel("● Отключено")
        self.status_label.setStyleSheet("color: #f44336; font-weight: bold;")

        layout.addWidget(QLabel("Порт:"))
        layout.addWidget(self.port_combo)
        layout.addWidget(self.refresh_btn)
        layout.addWidget(self.connect_btn)
        layout.addStretch()
        layout.addWidget(self.status_label)

        self._connected = False

    def set_ports(self, ports):
        self.port_combo.clear()
        self.port_combo.addItems(ports)

    def _on_connect_click(self):
        if self._connected:
            self.disconnect_requested.emit()
        else:
            port = self.port_combo.currentText()
            if port:
                self.connect_requested.emit(port)

    def set_connected_state(self, connected: bool):
        self._connected = connected
        if connected:
            self.status_label.setText("● Подключено")
            self.status_label.setStyleSheet("color: #4caf50; font-weight: bold;")
            self.connect_btn.setText("Отключить")
        else:
            self.status_label.setText("● Отключено")
            self.status_label.setStyleSheet("color: #f44336; font-weight: bold;")
            self.connect_btn.setText("Подключить")