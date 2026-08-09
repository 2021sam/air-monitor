import json
from pathlib import Path

SETTINGS_PATH = Path(__file__).resolve().parents[2] / "config" / "settings.json"

DEFAULTS = {
    "poll_seconds": 2,
    "warmup_seconds": 60 * 30,
    "chart_hours": 1,
}


def load_settings():
    if not SETTINGS_PATH.exists():
        save_settings(DEFAULTS)
        return DEFAULTS.copy()

    with SETTINGS_PATH.open() as f:
        data = json.load(f)

    return {**DEFAULTS, **data}


def save_settings(settings):
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with SETTINGS_PATH.open("w") as f:
        json.dump(settings, f, indent=2)
