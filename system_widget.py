from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout, QLabel, QListWidget


class SystemWidget(QWidget):
    """Информация о полётном контроллере и подключённых сенсорах.
    Только отображение — никаких настроек тут изменить нельзя."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        fc_group = QGroupBox("Полётный контроллер")
        form = QFormLayout(fc_group)
        self.variant_label = QLabel("--")
        self.version_label = QLabel("--")
        self.board_label = QLabel("--")
        self.armed_label = QLabel("--")
        self.profile_label = QLabel("--")
        form.addRow("Прошивка:", self.variant_label)
        form.addRow("Версия:", self.version_label)
        form.addRow("Плата:", self.board_label)
        form.addRow("Статус:", self.armed_label)
        form.addRow("Профиль:", self.profile_label)

        sensors_group = QGroupBox("Обнаруженные сенсоры")
        sensors_layout = QVBoxLayout(sensors_group)
        self.sensors_list = QListWidget()
        sensors_layout.addWidget(self.sensors_list)

        layout.addWidget(fc_group)
        layout.addWidget(sensors_group)
        layout.addStretch()

    def update_fc_info(self, variant=None, version=None, board=None):
        if variant:
            self.variant_label.setText(variant)
        if version:
            self.version_label.setText(version)
        if board:
            self.board_label.setText(board.get("board_id", "--"))

    def update_status(self, status: dict):
        self.armed_label.setText("Armed" if status["armed"] else "Disarmed")
        self.armed_label.setStyleSheet(
            "color: #f44336; font-weight: bold;" if status["armed"]
            else "color: #4caf50; font-weight: bold;"
        )
        self.profile_label.setText(str(status["profile"]))

        self.sensors_list.clear()
        for sensor in status["sensors"]:
            self.sensors_list.addItem(f"✓ {sensor}")