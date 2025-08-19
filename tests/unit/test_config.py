
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
