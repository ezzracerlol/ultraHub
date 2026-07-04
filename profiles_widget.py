from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox,
    QPushButton, QListWidget, QLabel, QMessageBox
)
from PyQt6.QtCore import pyqtSignal
from whoophub_profiles import load_profiles, add_profile, delete_profile, SIZES


class ProfilesWidget(QWidget):
    profile_selected = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)

        left = QVBoxLayout()
        left.addWidget(QLabel("Профили дронов:"))
        self.profile_list = QListWidget()
        self.profile_list.currentTextChanged.connect(self._on_select)
        self.use_btn = QPushButton("Использовать")
        self.use_btn.clicked.connect(self._use_profile)
        self.del_btn = QPushButton("Удалить")
        self.del_btn.clicked.connect(self._delete_profile)
        left.addWidget(self.profile_list)
        left.addWidget(self.use_btn)
        left.addWidget(self.del_btn)

        right = QGroupBox("Новый профиль")
        form = QFormLayout(right)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Например: Mobula6 HD")

        self.size_combo = QComboBox()
        self.size_combo.addItems(SIZES)

        self.cells_spin = QSpinBox()
        self.cells_spin.setRange(1, 6)
        self.cells_spin.setValue(1)
        self.cells_spin.valueChanged.connect(self._auto_voltage)

        self.full_v = QDoubleSpinBox()
        self.full_v.setRange(2.0, 26.0)
        self.full_v.setSingleStep(0.05)
        self.full_v.setValue(4.35)
        self.full_v.setSuffix(" В")

        self.warn_v = QDoubleSpinBox()
        self.warn_v.setRange(2.0, 25.0)
        self.warn_v.setSingleStep(0.05)
        self.warn_v.setValue(3.3)
        self.warn_v.setSuffix(" В")

        self.empty_v = QDoubleSpinBox()
        self.empty_v.setRange(2.0, 22.0)
        self.empty_v.setSingleStep(0.05)
        self.empty_v.setValue(3.0)
        self.empty_v.setSuffix(" В")

        form.addRow("Название:", self.name_edit)
        form.addRow("Размер:", self.size_combo)
        form.addRow("Банок:", self.cells_spin)
        form.addRow("Полный заряд:", self.full_v)
        form.addRow("Предупреждение:", self.warn_v)
        form.addRow("Разряжен:", self.empty_v)

        self.save_btn = QPushButton("Сохранить профиль")
        self.save_btn.clicked.connect(self._save_profile)
        form.addRow(self.save_btn)

        layout.addLayout(left, 1)
        layout.addWidget(right, 1)

        self._refresh_list()
        self._selected_profile = None

    def _auto_voltage(self, cells):
        self.full_v.setValue(round(4.35 * cells, 2))
        self.warn_v.setValue(round(3.3 * cells, 2))
        self.empty_v.setValue(round(3.0 * cells, 2))

    def _refresh_list(self):
        self.profile_list.clear()
        for p in load_profiles():
            self.profile_list.addItem(p["name"])

    def _on_select(self, name):
        from whoophub_profiles import get_profile
        self._selected_profile = get_profile(name)

    def _use_profile(self):
        if self._selected_profile:
            self.profile_selected.emit(self._selected_profile)
            QMessageBox.information(self, "Профиль", f"Активен: {self._selected_profile['name']}")

    def _delete_profile(self):
        if self._selected_profile:
            delete_profile(self._selected_profile["name"])
            self._selected_profile = None
            self._refresh_list()

    def _save_profile(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название дрона")
            return
        profile = {
            "name": name,
            "size": self.size_combo.currentText(),
            "cell_count": self.cells_spin.value(),
            "full_voltage": self.full_v.value(),
            "warn_voltage": self.warn_v.value(),
            "empty_voltage": self.empty_v.value(),
        }
        add_profile(profile)
        self._refresh_list()
        self.name_edit.clear()