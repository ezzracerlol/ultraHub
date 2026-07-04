from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QFormLayout, QLabel, QLineEdit, QPushButton
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt


FLY_LIMITS = {
    "1S Whoop 65mm":  {"wind_kmh": 5,  "visibility": 3},
    "1S Whoop 75mm":  {"wind_kmh": 7,  "visibility": 3},
    "2S Whoop 75mm":  {"wind_kmh": 9,  "visibility": 3},
    "2S Toothpick":   {"wind_kmh": 14, "visibility": 4},
    "3S 3inch":       {"wind_kmh": 18, "visibility": 5},
    "4S 5inch":       {"wind_kmh": 28, "visibility": 5},
    "6S 5inch":       {"wind_kmh": 33, "visibility": 5},
    "6S 7inch":       {"wind_kmh": 38, "visibility": 5},
    "Другой":         {"wind_kmh": 10, "visibility": 3},
}

DEFAULT_LIMITS = {"wind_kmh": 10, "visibility": 3}


class WeatherFetcher(QThread):
    result = pyqtSignal(dict)
    error  = pyqtSignal(str)

    def __init__(self, city):
        super().__init__()
        self.city = city

    def run(self):
        try:
            import urllib.request as ureq
            import urllib.parse as uparse
            import json as js
            url = "https://wttr.in/" + uparse.quote(self.city) + "?format=j1"
            req = ureq.Request(url, headers={"User-Agent": "WhoopHub/1.0"})
            with ureq.urlopen(req, timeout=8) as r:
                data = js.loads(r.read())
            cur = data["current_condition"][0]
            self.result.emit({
                "temp":     cur["temp_C"],
                "feels":    cur["FeelsLikeC"],
                "humidity": cur["humidity"],
                "wind_kmh": cur["windspeedKmph"],
                "wind_dir": cur["winddir16Point"],
                "desc":     cur["weatherDesc"][0]["value"],
                "vis":      cur["visibility"],
            })
        except Exception as e:
            self.error.emit(str(e))


class WeatherWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._active_profile = {"size": "1S Whoop 75mm"}
        layout = QVBoxLayout(self)

        search = QHBoxLayout()
        self.city_edit = QLineEdit()
        self.city_edit.setPlaceholderText("Введите город...")
        self.city_edit.returnPressed.connect(self._fetch)
        self.search_btn = QPushButton("Получить погоду")
        self.search_btn.clicked.connect(self._fetch)
        search.addWidget(self.city_edit)
        search.addWidget(self.search_btn)
        layout.addLayout(search)

        # Текущий профиль и лимиты
        self.profile_label = QLabel("Дрон: 1S Whoop 75mm  |  Макс. ветер: 7 км/ч")
        self.profile_label.setStyleSheet("color: #4fc3f7; font-size: 12px; padding: 4px;")
        layout.addWidget(self.profile_label)

        weather_group = QGroupBox("Текущая погода")
        wform = QFormLayout(weather_group)
        self.desc_lbl  = QLabel("—")
        self.temp_lbl  = QLabel("—")
        self.feels_lbl = QLabel("—")
        self.humid_lbl = QLabel("—")
        self.wind_lbl  = QLabel("—")
        self.vis_lbl   = QLabel("—")
        wform.addRow("Погода:",        self.desc_lbl)
        wform.addRow("Температура:",   self.temp_lbl)
        wform.addRow("Ощущается как:", self.feels_lbl)
        wform.addRow("Влажность:",     self.humid_lbl)
        wform.addRow("Ветер:",         self.wind_lbl)
        wform.addRow("Видимость:",     self.vis_lbl)

        fly_group = QGroupBox("Пригодность для полётов FPV")
        fly_layout = QVBoxLayout(fly_group)
        self.fly_status = QLabel("Введите город для оценки")
        self.fly_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fly_status.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        self.wind_warn = QLabel("")
        self.vis_warn  = QLabel("")
        fly_layout.addWidget(self.fly_status)
        fly_layout.addWidget(self.wind_warn)
        fly_layout.addWidget(self.vis_warn)

        layout.addWidget(weather_group)
        layout.addWidget(fly_group)
        layout.addStretch()

        self._fetcher = None
        self._last_data = None

    def set_profile(self, profile):
        self._active_profile = profile
        size = profile.get("size", "Другой")
        limits = FLY_LIMITS.get(size, DEFAULT_LIMITS)
        self.profile_label.setText(
            f"Дрон: {profile.get('name', size)}  |  "
            f"Макс. ветер: {limits['wind_kmh']} км/ч  |  "
            f"Мин. видимость: {limits['visibility']} км"
        )
        # Пересчитать если данные уже есть
        if self._last_data:
            self._show(self._last_data)

    def _get_limits(self):
        size = self._active_profile.get("size", "Другой")
        return FLY_LIMITS.get(size, DEFAULT_LIMITS)

    def _fetch(self):
        city = self.city_edit.text().strip()
        if not city:
            return
        self.search_btn.setEnabled(False)
        self.fly_status.setText("Загрузка...")
        self._fetcher = WeatherFetcher(city)
        self._fetcher.result.connect(self._show)
        self._fetcher.error.connect(self._err)
        self._fetcher.start()

    def _show(self, d):
        self._last_data = d
        self.search_btn.setEnabled(True)
        self.desc_lbl.setText(d["desc"])
        self.temp_lbl.setText(f"{d['temp']} °C")
        self.feels_lbl.setText(f"{d['feels']} °C")
        self.humid_lbl.setText(f"{d['humidity']} %")
        self.wind_lbl.setText(f"{d['wind_kmh']} км/ч  {d['wind_dir']}")
        self.vis_lbl.setText(f"{d['vis']} км")

        limits = self._get_limits()
        wind = int(d["wind_kmh"])
        vis  = int(d["vis"])
        ok   = True

        if wind > limits["wind_kmh"]:
            self.wind_warn.setText(f"⚠️ Ветер {wind} км/ч — слишком сильный! (лимит {limits['wind_kmh']} км/ч)")
            self.wind_warn.setStyleSheet("color: #f44336;")
            ok = False
        else:
            self.wind_warn.setText(f"✅ Ветер {wind} км/ч — норм (лимит {limits['wind_kmh']} км/ч)")
            self.wind_warn.setStyleSheet("color: #4caf50;")

        if vis < limits["visibility"]:
            self.vis_warn.setText(f"⚠️ Видимость {vis} км — плохая! (мин. {limits['visibility']} км)")
            self.vis_warn.setStyleSheet("color: #f44336;")
            ok = False
        else:
            self.vis_warn.setText(f"✅ Видимость {vis} км — хорошая")
            self.vis_warn.setStyleSheet("color: #4caf50;")

        if ok:
            self.fly_status.setText("✅ Можно летать!")
            self.fly_status.setStyleSheet(
                "font-size:16px;font-weight:bold;color:#4caf50;padding:10px;"
            )
        else:
            self.fly_status.setText("⛔ Лучше не летать")
            self.fly_status.setStyleSheet(
                "font-size:16px;font-weight:bold;color:#f44336;padding:10px;"
            )

    def _err(self, msg):
        self.search_btn.setEnabled(True)
        self.fly_status.setText(f"Ошибка: {msg}")
        self.fly_status.setStyleSheet("color:#f44336;font-size:13px;padding:10px;")