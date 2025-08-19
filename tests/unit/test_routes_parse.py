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
