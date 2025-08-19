from app import create_app

def _post(client, data):
    return client.post("/", data=data, follow_redirects=True)

def test_validation_sum_to_100():
    app = create_app({"TESTING": True})
    with app.test_client() as client:
        resp = _post(client, {
            "tasks[]": ["A", "B"],
            "percentages[]": ["60", "30"],
            "available_days": "2",
            "hours_per_day": "8",
        })
        assert resp.status_code == 200
        assert b"Percentages must sum to 100" in resp.data

def test_happy_path_renders_table():
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
        assert "Results" in html
        assert "Alpha" in html
        assert "Beta" in html
        # Header should include 'Day 1' and 'Day 2' prepared by the route (no Jinja range/zip).
        assert "Day 1" in html
        assert "Day 2" in html


def test_empty_task_name_errors():
    app = create_app({"TESTING": True})
    with app.test_client() as client:
        resp = _post(client, {
            "tasks[]": ["A", ""],
            "percentages[]": ["60", "40"],
            "available_days": "3",
            "hours_per_day": "8",
        })
        assert resp.status_code == 200
        html = resp.data.decode()
        assert "Please fill all tasks names" in html
        assert "Results" not in html


def test_duplicate_tasks_errors():
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


def test_invalid_percentage_and_sum_error():
    app = create_app({"TESTING": True})
    with app.test_client() as client:
        resp = _post(client, {
            "tasks[]": ["A", "B"],
            "percentages[]": ["abc", "20"],  # invalid and totals != 100
            "available_days": "2",
            "hours_per_day": "8",
        })
        assert resp.status_code == 200
        html = resp.data.decode()
        assert "Invalid percentage for task #1." in html
        assert "Percentages must sum to 100." in html
        assert "Results" not in html


def test_zero_days_and_hours_errors():
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


def test_task_options_exposed_in_get_contains_resource_values():
    app = create_app({"TESTING": True})
    with app.test_client() as client:
        rv = client.get("/")
        assert rv.status_code == 200
        html = rv.data.decode()
        # resources/tasks.csv contains codes like 05882; ensure present in data-options JSON
        assert "data-options" in html
        assert "05882" in html


def test_preserves_submitted_values_on_error():
    app = create_app({"TESTING": True})
    with app.test_client() as client:
        # Trigger an error (duplicate tasks) while submitting custom numeric fields
        resp = _post(client, {
            "tasks[]": ["X", "X"],
            "percentages[]": ["10", "90"],
            "available_days": "13",
            "hours_per_day": "17",
        })
        assert resp.status_code == 200
        html = resp.data.decode()
        # Form should reflect submitted numbers back into the inputs
        assert 'name="available_days"' in html and 'value="13"' in html
        assert 'name="hours_per_day"' in html and 'value="17"' in html

