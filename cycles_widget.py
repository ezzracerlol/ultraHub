from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
    QLineEdit, QPushButton, QListWidget, QLabel, QListWidgetItem,
    QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt
from battery_cycles import load_cycles, add_cycle, delete_battery, get_battery


class CyclesWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)

        # Левая панель — список батарей
        left = QVBoxLayout()
        left.addWidget(QLabel("Мои батареи:"))
        self.bat_list = QListWidget()
        self.bat_list.currentTextChanged.connect(self._on_select)
        left.addWidget(self.bat_list)

        btn_row = QHBoxLayout()
        self.del_btn = QPushButton("Удалить")
        self.del_btn.clicked.connect(self._delete)
        btn_row.addWidget(self.del_btn)
        left.addLayout(btn_row)

        # Правая панель — детали + добавление
        right = QVBoxLayout()

        info_group = QGroupBox("Информация о батарее")
        info_form = QFormLayout(info_group)
        self.name_label = QLabel("—")
        self.cycles_label = QLabel("—")
        self.cycles_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #4fc3f7;")
        self.health_bar = QProgressBar()
        self.health_bar.setRange(0, 100)
        self.health_bar.setTextVisible(True)
        self.last_label = QLabel("—")
        self.add_cycle_btn = QPushButton("+ Добавить цикл заряда")
        self.add_cycle_btn.clicked.connect(self._add_cycle)
        self.add_cycle_btn.setEnabled(False)
        info_form.addRow("Батарея:", self.name_label)
        info_form.addRow("Циклов:", self.cycles_label)
        info_form.addRow("Здоровье:", self.health_bar)
        info_form.addRow("Последний заряд:", self.last_label)
        info_form.addRow(self.add_cycle_btn)

        new_group = QGroupBox("Добавить батарею")
        new_form = QFormLayout(new_group)
        self.new_name = QLineEdit()
        self.new_name.setPlaceholderText("Например: GNB 300mAh #1")
        self.save_btn = QPushButton("Сохранить")
        self.save_btn.clicked.connect(self._save_new)
        new_form.addRow("Название:", self.new_name)
        new_form.addRow(self.save_btn)

        right.addWidget(info_group)
        right.addWidget(new_group)
        right.addStretch()

        layout.addLayout(left, 1)
        layout.addLayout(right, 2)

        self._selected = None
        self._refresh()

    def _refresh(self):
        self.bat_list.clear()
        for name, data in load_cycles().items():
            item = QListWidgetItem(f"{name}  ({data['cycles']} цикл.)")
            self.bat_list.addItem(item)

    def _on_select(self, text):
        if not text:
            return
        name = text.split("  (")[0]
        self._selected = name
        data = get_battery(name)
        cycles = data["cycles"]
        self.name_label.setText(name)
        self.cycles_label.setText(str(cycles))
        self.add_cycle_btn.setEnabled(True)

        # Здоровье: до 50 циклов = хорошо, 50-100 = средне, 100+ = плохо
        health = max(0, 100 - cycles)
        self.health_bar.setValue(health)
        if health > 60:
            color = "#4caf50"
        elif health > 30:
            color = "#ff9800"
        else:
            color = "#f44336"
        self.health_bar.setStyleSheet(
            f"QProgressBar::chunk {{ background-color: {color}; border-radius: 3px; }}"
        )
        self.health_bar.setFormat(f"{health}%")

        history = data.get("history", [])
        self.last_label.setText(history[-1] if history else "—")

    def _add_cycle(self):
        if self._selected:
            cycles = add_cycle(self._selected)
            self._refresh()
            self.cycles_label.setText(str(cycles))

    def _save_new(self):
        name = self.new_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название батареи")
            return
        add_cycle.__module__
        from battery_cycles import load_cycles, save_cycles
        data = load_cycles()
        if name not in data:
            data[name] = {"cycles": 0, "history": []}
            save_cycles(data)
        self.new_name.clear()
        self._refresh()

    def _delete(self):
        if self._selected:
            delete_battery(self._selected)
            self._selected = None
            self.name_label.setText("—")
            self.cycles_label.setText("—")
            self.add_cycle_btn.setEnabled(False)
            self._refresh()