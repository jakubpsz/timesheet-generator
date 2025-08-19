
from app.config import load_config
from pathlib import Path
import textwrap

def test_load_config_from_ini(tmp_path):
    cfg = tmp_path / "config.ini"
    cfg.write_text(textwrap.dedent('''
        [DEFAULTS]
        available_days = 3
        hours_per_day = 6
    '''))
    data = load_config(cfg)
    assert data["AVAILABLE_DAYS"] == 3
    assert data["HOURS_PER_DAY"] == 6

def test_env_overrides_defaults_and_file(monkeypatch, tmp_path):
    # Create a config file with values that should be overridden by env
    cfg = tmp_path / "config.ini"
    cfg.write_text("""
        [DEFAULTS]
        available_days = 1
        hours_per_day = 2
    """.strip())

    monkeypatch.setenv("AVAILABLE_DAYS", "7")
    monkeypatch.setenv("HOURS_PER_DAY", "9")

    data = load_config(cfg)
    assert data["AVAILABLE_DAYS"] == 7
    assert data["HOURS_PER_DAY"] == 9


def test_defaults_used_when_file_missing(tmp_path, monkeypatch):
    # Ensure no env overrides
    monkeypatch.delenv("AVAILABLE_DAYS", raising=False)
    monkeypatch.delenv("HOURS_PER_DAY", raising=False)

    # Point to a non-existent ini file
    cfg = tmp_path / "missing.ini"
    data = load_config(cfg)
    # Defaults from DEFAULT_CONFIG in app/config.py
    assert data["AVAILABLE_DAYS"] == 5
    assert data["HOURS_PER_DAY"] == 8


def test_file_values_used_without_env(tmp_path, monkeypatch):
    monkeypatch.delenv("AVAILABLE_DAYS", raising=False)
    monkeypatch.delenv("HOURS_PER_DAY", raising=False)

    cfg = tmp_path / "config.ini"
    cfg.write_text("""
        [DEFAULTS]
        available_days = 6
        hours_per_day = 10
    """.strip())

    data = load_config(cfg)
    assert data["AVAILABLE_DAYS"] == 6
    assert data["HOURS_PER_DAY"] == 10
