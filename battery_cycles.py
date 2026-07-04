import json
import os
from datetime import datetime

CYCLES_PATH = os.path.join(os.path.dirname(__file__), "battery_cycles.json")


def load_cycles():
    try:
        with open(CYCLES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_cycles(data):
    with open(CYCLES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_battery(name):
    return load_cycles().get(name, {"cycles": 0, "history": []})


def add_cycle(name):
    data = load_cycles()
    if name not in data:
        data[name] = {"cycles": 0, "history": []}
    data[name]["cycles"] += 1
    data[name]["history"].append(datetime.now().strftime("%Y-%m-%d %H:%M"))
    save_cycles(data)
    return data[name]["cycles"]


def delete_battery(name):
    data = load_cycles()
    if name in data:
        del data[name]
        save_cycles(data)


def all_batteries():
    return load_cycles()