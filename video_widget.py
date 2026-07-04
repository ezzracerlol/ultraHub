import cv2
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap


class VideoWidget(QWidget):
    """Просмотр видео с FPV-приёмника/камеры захвата. Только отображение потока."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        top_row = QHBoxLayout()
        self.device_combo = QComboBox()
        self.device_combo.addItems([f"Камера {i}" for i in range(4)])
        self.start_btn = QPushButton("Запустить просмотр")
        self.stop_btn = QPushButton("Остановить")
        self.stop_btn.setEnabled(False)
        top_row.addWidget(QLabel("Источник:"))
        top_row.addWidget(self.device_combo)
        top_row.addWidget(self.start_btn)
        top_row.addWidget(self.stop_btn)
        top_row.addStretch()

        self.video_label = QLabel("Видео не запущено")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumSize(640, 360)
        self.video_label.setStyleSheet("background-color: black; color: #7a7d81;")

        layout.addLayout(top_row)
        layout.addWidget(self.video_label)

        self.start_btn.clicked.connect(self.start_stream)
        self.stop_btn.clicked.connect(self.stop_stream)

        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_frame)

    def start_stream(self):
        idx = self.device_combo.currentIndex()
        self.cap = cv2.VideoCapture(idx)
        if not self.cap.isOpened():
            self.video_label.setText("Не удалось открыть источник видео")
            self.cap = None
            return
        self.timer.start(33)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def stop_stream(self):
        self.timer.stop()
        if self.cap:
            self.cap.release()
            self.cap = None
        self.video_label.setText("Видео остановлено")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def _update_frame(self):
        if not self.cap:
            return
        ret, frame = self.cap.read()
        if not ret:
            return
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        img = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(img).scaled(
            self.video_label.width(), self.video_label.height(),
            Qt.AspectRatioMode.KeepAspectRatio
        )
        self.video_label.setPixmap(pixmap)

    def closeEvent(self, event):
        self.stop_stream()
        super().closeEvent(event)