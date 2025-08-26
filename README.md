
# Time sheet generator

## How to run
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=run:app
flask run --host=0.0.0.0 --port=80
```

## How to run test
```bash
python -m pytest --cov=app --cov-report=html
```
