import json
import os

PROFILES_PATH = os.path.join(os.path.dirname(__file__), "whoophub_profiles.json")

DEFAULT_PROFILES = [
    {
        "name": "BetaFPV Air75 II Champion",
        "size": "1S Whoop 75mm",
        "cell_count": 1,
        "full_voltage": 4.35,
        "empty_voltage": 3.0,
        "warn_voltage": 3.3,
    }
]

SIZES = [
    "1S Whoop 65mm",
    "1S Whoop 75mm",
    "2S Whoop 75mm",
    "2S Toothpick",
    "3S 3inch",
    "4S 5inch",
    "6S 5inch",
    "6S 7inch",
    "Другой",
]


def load_profiles():
    try:
        with open(PROFILES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        save_profiles(DEFAULT_PROFILES)
        return DEFAULT_PROFILES


def save_profiles(profiles):
    with open(PROFILES_PATH, "w", encoding="utf-8") as f:
        json.dump(profiles, f, ensure_ascii=False, indent=2)


def add_profile(profile):
    profiles = load_profiles()
    profiles.append(profile)
    save_profiles(profiles)


def delete_profile(name):
    profiles = [p for p in load_profiles() if p["name"] != name]
    save_profiles(profiles)


def get_profile(name):
    for p in load_profiles():
        if p["name"] == name:
            return p
    return None