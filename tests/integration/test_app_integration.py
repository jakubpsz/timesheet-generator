from app import create_app


def _post(client, data):
    return client.post("/", data=data, follow_redirects=True)


def test_index_get():
    app = create_app({"TESTING": True})
    with app.test_client() as client:
        rv = client.get("/")
        assert rv.status_code == 200


def test_index_get_includes_defaults_and_task_options():
    app = create_app({"TESTING": True})
    with app.test_client() as client:
        rv = client.get("/")
        assert rv.status_code == 200
        html = rv.data.decode()
        # Defaults from config.ini should be reflected in inputs
        assert 'name="available_days"' in html and 'value="5"' in html
        assert 'name="hours_per_day"' in html and 'value="8"' in html
        # Task options from resources/tasks.csv should be embedded as JSON
        assert 'data-options' in html
        assert '05882' in html


def test_post_invalid_duplicate_tasks_shows_errors_no_results():
    app = create_app({"TESTING": True})
    with app.test_client() as client:
        resp = _post(client, {
            "tasks[]": ["A", "A"],
            "percentages[]": ["50", "50"],
            "available_days": "2",
            "hours_per_day": "8",
        })
        assert resp.status_code == 200
        html = resp.data.decode()
        assert "A task was selected more than once." in html
        assert "Results" not in html


def test_post_invalid_zero_days_hours_shows_errors():
    app = create_app({"TESTING": True})
    with app.test_client() as client:
        resp = _post(client, {
            "tasks[]": ["A", "B"],
            "percentages[]": ["50", "50"],
            "available_days": "0",
            "hours_per_day": "0",
        })
        assert resp.status_code == 200
        html = resp.data.decode()
        assert "Available days must be a positive integer." in html
        assert "Hours per day must be a positive integer." in html
        assert "Results" not in html


def test_post_valid_shows_table_totals_and_formatted_cells():
    app = create_app({"TESTING": True})
    with app.test_client() as client:
        resp = _post(client, {
            "tasks[]": ["Alpha", "Beta"],
            "percentages[]": ["50", "50"],
            "available_days": "2",
            "hours_per_day": "8",
        })
        assert resp.status_code == 200
        html = resp.data.decode()
        # Table and headers
        assert "Results" in html
        assert "Day 1" in html and "Day 2" in html
        assert "<th>Total hours</th>" in html
        # Rows and totals
        assert "Alpha" in html and "Beta" in html
        # Grand total should be 16.00 (2 days * 8 hours)
        assert "16.00" in html
        # Cells should be formatted to 2 decimals and include 8.00 and 0.00 for this split
        assert "8.00" in html
        assert "0.00" in html


def test_env_overrides_defaults_integration(monkeypatch):
    # Ensure environment variables override config.ini defaults for GET form
    monkeypatch.setenv("AVAILABLE_DAYS", "7")
    monkeypatch.setenv("HOURS_PER_DAY", "9")

    app = create_app({"TESTING": True})
    with app.test_client() as client:
        rv = client.get("/")
        assert rv.status_code == 200
        html = rv.data.decode()
        assert 'name="available_days"' in html and 'value="7"' in html
        assert 'name="hours_per_day"' in html and 'value="9"' in html
