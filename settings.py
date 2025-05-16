import json
import os

SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "speed": "Средне",
    "sound": True,
    "theme": "Классическая",
    "retro_style": False,
    "sound_effects": True}

def load_settings():

    default_settings = {
        "sound_effects": True,
        "background_music": True,
        "theme": "Тёмная",
        "retro_style": False
    }
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)
