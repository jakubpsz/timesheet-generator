from app import create_app

def test_index_get():
    app = create_app({"TESTING": True})
    with app.test_client() as client:
        rv = client.get("/")
        assert rv.status_code == 200

def test_full_flow_renders_rows_and_headers():
    app = create_app({"TESTING": True})
    with app.test_client() as client:
        rv = client.post("/", data={
            "tasks[]": ["Task 1", "Task 2"],
            "percentages[]": ["70", "30"],
            "available_days": "3",
            "hours_per_day": "6",
        })
        assert rv.status_code == 200
        html = rv.data.decode()
        assert "Results" in html
        assert "Task 1" in html
        assert "Task 2" in html
        # Check that the table header shows explicit day labels (coming from the route)
        assert "Day 1" in html and "Day 2" in html and "Day 3" in html
