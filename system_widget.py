from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt


def small_label(text):
    l = QLabel(text)
    l.setStyleSheet("color:#555;font-size:10px;letter-spacing:2px;background:transparent;border:none;")
    return l


def card(parent=None):
    w = QWidget(parent)
    w.setStyleSheet("background:#111318;border-radius:8px;border:1px solid #1e222a;")
    l = QVBoxLayout(w)
    l.setContentsMargins(14, 12, 14, 12)
    l.setSpacing(8)
    return w, l


def info_row(key, val_text, key_color="#444", val_color="#ccc"):
    row = QHBoxLayout()
    k = QLabel(key)
    k.setStyleSheet(f"color:{key_color};font-size:11px;background:transparent;")
    v = QLabel(val_text)
    v.setAlignment(Qt.AlignmentFlag.AlignRight)
    v.setStyleSheet(f"color:{val_color};font-size:11px;font-weight:600;background:transparent;")
    row.addWidget(k)
    row.addStretch()
    row.addWidget(v)
    return row, v


class SystemWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:#0d0e10;")
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        # Заголовок
        hdr = QHBoxLayout()
        dot = QLabel("●")
        dot.setStyleSheet("color:#4fc3f7;font-size:10px;background:transparent;")
        title = QLabel("СИСТЕМА / FC INFO")
        title.setStyleSheet("color:#4fc3f7;font-size:13px;font-weight:700;letter-spacing:2px;background:transparent;")
        self.status_lbl = QLabel("DISARMED")
        self.status_lbl.setStyleSheet(
            "color:#4caf50;background:#1a2a1a;border:1px solid #2a5a2a;"
            "border-radius:4px;padding:2px 10px;font-size:11px;letter-spacing:1px;"
        )
        hdr.addWidget(dot)
        hdr.addWidget(title)
        hdr.addStretch()
        hdr.addWidget(self.status_lbl)
        root.addLayout(hdr)

        # Строка 1: FC + Плата
        row1 = QHBoxLayout()
        row1.setSpacing(8)

        fc_w, fcl = card()
        fcl.addWidget(small_label("ПОЛЁТНЫЙ КОНТРОЛЛЕР"))
        r1, self.variant_val = info_row("Прошивка", "--", val_color="#4fc3f7")
        r2, self.version_val = info_row("Версия", "--")
        r3, self.board_val   = info_row("Плата", "--")
        r4, self.profile_val = info_row("Профиль", "--")
        r5, self.i2c_val     = info_row("I2C ошибки", "--", val_color="#ff9800")
        for r in [r1, r2, r3, r4, r5]:
            fcl.addLayout(r)

        sensors_w, sl = card()
        sl.addWidget(small_label("ОБНАРУЖЕННЫЕ СЕНСОРЫ"))
        self.sensor_grid = QGridLayout()
        self.sensor_grid.setSpacing(6)
        self.sensor_labels = {}
        sensors = [
            ("GYRO",  "Гироскоп"),
            ("ACC",   "Акселерометр"),
            ("BARO",  "Барометр"),
            ("MAG",   "Магнитометр"),
            ("GPS",   "GPS"),
            ("RANGE", "Датчик дальности"),
        ]
        for i, (code, name) in enumerate(sensors):
            lbl_code = QLabel(code)
            lbl_code.setStyleSheet(
                "background:#1a1e2a;border:1px solid #2a2e3a;border-radius:4px;"
                "padding:3px 8px;font-size:10px;color:#444;font-weight:600;"
            )
            lbl_name = QLabel(name)
            lbl_name.setStyleSheet("color:#444;font-size:10px;background:transparent;")
            self.sensor_grid.addWidget(lbl_code, i, 0)
            self.sensor_grid.addWidget(lbl_name, i, 1)
            self.sensor_labels[name] = lbl_code
        sl.addLayout(self.sensor_grid)
        sl.addStretch()

        row1.addWidget(fc_w, 1)
        row1.addWidget(sensors_w, 1)
        root.addLayout(row1)

        # Строка 2: Статистика полёта
        stats_w, stl = card()
        stl.addWidget(small_label("СТАТУС"))
        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)

        for label, attr in [
            ("Профиль PID", "pid_lbl"),
            ("Цикл (мкс)", "cycle_lbl"),
            ("Статус", "mode_lbl"),
        ]:
            col = QVBoxLayout()
            title_l = QLabel(label)
            title_l.setStyleSheet("color:#555;font-size:10px;letter-spacing:1px;background:transparent;")
            val_l = QLabel("--")
            val_l.setStyleSheet("color:#4fc3f7;font-size:20px;font-weight:700;background:transparent;")
            col.addWidget(title_l)
            col.addWidget(val_l)
            stats_row.addLayout(col)
            setattr(self, attr, val_l)

        stl.addLayout(stats_row)
        root.addWidget(stats_w)
        root.addStretch()

    def update_fc_info(self, variant=None, version=None, board=None):
        if variant:
            self.variant_val.setText(variant)
        if version:
            self.version_val.setText(version)
        if board:
            self.board_val.setText(board.get("board_id", "--"))

    def update_status(self, status):
        armed = status.get("armed", False)
        self.status_lbl.setText("ARMED" if armed else "DISARMED")
        self.status_lbl.setStyleSheet(
            "color:#f44336;background:#2a1a1a;border:1px solid #5a2a2a;"
            "border-radius:4px;padding:2px 10px;font-size:11px;letter-spacing:1px;"
            if armed else
            "color:#4caf50;background:#1a2a1a;border:1px solid #2a5a2a;"
            "border-radius:4px;padding:2px 10px;font-size:11px;letter-spacing:1px;"
        )
        self.profile_val.setText(str(status.get("profile", "--")))
        self.i2c_val.setText(str(status.get("i2c_errors", 0)))
        self.mode_lbl.setText("ARMED" if armed else "DISARMED")
        self.mode_lbl.setStyleSheet(
            f"color:{'#f44336' if armed else '#4caf50'};"
            "font-size:20px;font-weight:700;background:transparent;"
        )

        active = status.get("sensors", [])
        for name, lbl in self.sensor_labels.items():
            if name in active:
                lbl.setStyleSheet(
                    "background:#1a2a1a;border:1px solid #2a5a2a;border-radius:4px;"
                    "padding:3px 8px;font-size:10px;color:#4caf50;font-weight:600;"
                )
            else:
                lbl.setStyleSheet(
                    "background:#1a1e2a;border:1px solid #2a2e3a;border-radius:4px;"
                    "padding:3px 8px;font-size:10px;color:#444;font-weight:600;"
                )