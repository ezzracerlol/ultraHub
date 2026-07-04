from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QCheckBox, QPushButton, QLabel, QProgressBar
)
from PyQt6.QtCore import Qt


CHECKLIST = [
    ("Батарея", [
        "АКБ полностью заряжена",
        "Напряжение проверено",
        "АКБ надёжно зафиксирована",
    ]),
    ("Механика", [
        "Пропеллеры целые, без трещин",
        "Пропеллеры затянуты",
        "Моторы крутятся свободно",
        "Рама без повреждений",
        "Дакты целые",
    ]),
    ("Электроника", [
        "Камера работает",
        "Видеосигнал чистый",
        "Приёмник видит передатчик",
        "Все каналы RC откликаются",
        "Armed/disarmed работает",
    ]),
    ("Место полёта", [
        "Зона безопасна для полётов",
        "Нет людей в зоне полёта",
        "Погода подходящая",
        "Место посадки определено",
    ]),
]


class ChecklistWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Прогресс
        top = QHBoxLayout()
        self.progress_label = QLabel("Готовность: 0%")
        self.progress_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(False)
        self.reset_btn = QPushButton("Сбросить всё")
        self.reset_btn.clicked.connect(self._reset)
        top.addWidget(self.progress_label)
        top.addWidget(self.progress_bar, 1)
        top.addWidget(self.reset_btn)
        layout.addLayout(top)

        self.status_label = QLabel("⚠️ Не готов к полёту")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(
            "font-size: 15px; font-weight: bold; color: #f44336; padding: 6px;"
        )
        layout.addWidget(self.status_label)

        # Чекбоксы по группам
        self._checkboxes = []
        groups_layout = QHBoxLayout()

        for group_name, items in CHECKLIST:
            group = QGroupBox(group_name)
            g_layout = QVBoxLayout(group)
            for item in items:
                cb = QCheckBox(item)
                cb.stateChanged.connect(self._update_progress)
                g_layout.addWidget(cb)
                self._checkboxes.append(cb)
            g_layout.addStretch()
            groups_layout.addWidget(group)

        layout.addLayout(groups_layout)
        layout.addStretch()
        self._update_progress()

    def _update_progress(self):
        total = len(self._checkboxes)
        checked = sum(1 for cb in self._checkboxes if cb.isChecked())
        pct = int(checked / total * 100) if total else 0
        self.progress_bar.setValue(pct)
        self.progress_label.setText(f"Готовность: {pct}%")

        if pct < 60:
            color = "#f44336"
            self.progress_bar.setStyleSheet(
                "QProgressBar::chunk { background-color: #f44336; border-radius: 3px; }"
            )
            self.status_label.setText("⚠️ Не готов к полёту")
            self.status_label.setStyleSheet(
                "font-size: 15px; font-weight: bold; color: #f44336; padding: 6px;"
            )
        elif pct < 100:
            self.progress_bar.setStyleSheet(
                "QProgressBar::chunk { background-color: #ff9800; border-radius: 3px; }"
            )
            self.status_label.setText("🔶 Почти готов, проверь оставшееся")
            self.status_label.setStyleSheet(
                "font-size: 15px; font-weight: bold; color: #ff9800; padding: 6px;"
            )
        else:
            self.progress_bar.setStyleSheet(
                "QProgressBar::chunk { background-color: #4caf50; border-radius: 3px; }"
            )
            self.status_label.setText("✅ Готов к полёту!")
            self.status_label.setStyleSheet(
                "font-size: 15px; font-weight: bold; color: #4caf50; padding: 6px;"
            )

    def _reset(self):
        for cb in self._checkboxes:
            cb.setChecked(False)