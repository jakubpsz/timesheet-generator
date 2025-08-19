
import math
from app.services.scheduler import compute_schedule

def test_compute_schedule_distribution():
    tasks = ["A", "B", "C"]
    percentages = [25, 50, 25]
    task_hours, schedule = compute_schedule(tasks, percentages, available_days=4, hours_per_day=8)
    assert len(task_hours) == 3
    assert math.isclose(sum(task_hours), 32.0, rel_tol=1e-6)
    assert math.isclose(task_hours[0], 8.0, rel_tol=1e-6)
    assert math.isclose(task_hours[1], 16.0, rel_tol=1e-6)
    assert math.isclose(task_hours[2], 8.0, rel_tol=1e-6)
    assert len(schedule) == 3 and len(schedule[0]) == 4
