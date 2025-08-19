
# Refactored Flask App

## How to run
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=run:app
flask run --host=0.0.0.0 --port=80
```

## Configuration
Defaults are in `config.ini` (available_days, hours_per_day). Env vars `AVAILABLE_DAYS` and `HOURS_PER_DAY` override.

## Structure (Factory + Blueprints)
- `app/__init__.py` – app factory
- `app/config.py` – INI loader
- `app/services/` – business logic (e.g., `scheduler.py`)
- `app/main/` – blueprint (`routes.py`, templates, static)
- `wsgi.py` – production entrypoint
- `tests/` – unit and integration tests
- `requirements.txt` – dependencies

## Frontend
Uses Bootstrap 5, centered content, mobile-first.
```
app/main/templates/htm/ (Jinja templates)
app/main/static/css/styles.css
app/main/static/js/main.js
```
