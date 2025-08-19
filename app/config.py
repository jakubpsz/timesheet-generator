
"""
App configuration module.
Loads defaults from config.ini and environment variables.
"""
from __future__ import annotations
import os
import configparser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # project root

DEFAULT_CONFIG = {
    "DEFAULTS": {
        "available_days": "5",
        "hours_per_day": "8",
    }
}

def load_config(config_path: Path | None = None) -> dict:
    """
    Load config from an INI file and env vars.
    Env vars (AVAILABLE_DAYS, HOURS_PER_DAY) override file values.
    Returns a simple dict you can feed into app.config.update(...).
    """
    if config_path is None:
        # Look for config.ini in project root
        config_path = BASE_DIR / "config.ini"

    parser = configparser.ConfigParser()
    parser.read_dict(DEFAULT_CONFIG)
    if config_path.exists():
        parser.read(config_path)

    # Extract typed values
    available_days = int(os.getenv("AVAILABLE_DAYS", parser.get("DEFAULTS", "available_days", fallback="5")))
    hours_per_day = int(os.getenv("HOURS_PER_DAY", parser.get("DEFAULTS", "hours_per_day", fallback="8")))

    return {
        "AVAILABLE_DAYS": available_days,
        "HOURS_PER_DAY": hours_per_day,
    }
