import serial
import serial.tools.list_ports
from PyQt6.QtCore import QObject, pyqtSignal


class WhoopHubSerial(QObject):
    connected = pyqtSignal(bool)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.ser = None

    @staticmethod
    def list_ports():
        return [p.device for p in serial.tools.list_ports.comports()]

    def connect(self, port, baudrate=115200, timeout=0.5):
        try:
            self.ser = serial.Serial(port, baudrate, timeout=timeout)
            self.connected.emit(True)
            return True
        except Exception as e:
            self.error_occurred.emit(str(e))
            self.connected.emit(False)
            return False

    def disconnect(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.connected.emit(False)

    def is_connected(self):
        return self.ser is not None and self.ser.is_open

    def write(self, data: bytes):
        if self.is_connected():
            self.ser.write(data)

    def read_all(self):
        if self.is_connected() and self.ser.in_waiting:
            return self.ser.read(self.ser.in_waiting)
        return b""