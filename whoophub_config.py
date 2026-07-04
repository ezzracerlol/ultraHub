import json
import os

CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "config", "settings.json"
)

_DEFAULTS = {
    "drone_name": "BetaFPV Air75 II Champion",
    "battery": {"cell_count": 1, "full_voltage": 4.35, "empty_voltage": 3.0, "warn_voltage": 3.3},
    "serial": {"baudrate": 115200},
}


def load_whoophub_config() -> dict:
    """Загружает локальные настройки ОТОБРАЖЕНИЯ приложения.
    Никак не связано с настройками полётного контроллера."""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        merged = dict(_DEFAULTS)
        merged.update(data)
        return merged
    except Exception:
        return _DEFAULTS