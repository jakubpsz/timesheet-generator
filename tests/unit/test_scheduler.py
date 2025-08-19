
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

def test_single_task_equal_distribution():
    tasks = ["Only"]
    percentages = [100]
    task_hours, schedule = compute_schedule(tasks, percentages, available_days=3, hours_per_day=4)
    assert len(task_hours) == 1 and math.isclose(task_hours[0], 12.0, rel_tol=1e-6)
    assert schedule == [[4.0, 4.0, 4.0]]


def test_zero_percent_task_included():
    tasks = ["A", "B"]
    percentages = [0, 100]
    task_hours, schedule = compute_schedule(tasks, percentages, available_days=2, hours_per_day=5)
    assert math.isclose(task_hours[0], 0.0, rel_tol=1e-6)
    assert math.isclose(task_hours[1], 10.0, rel_tol=1e-6)
    assert schedule[0] == [0.0, 0.0]
    assert schedule[1] == [5.0, 5.0]


def test_tasks_spill_over_days_distribution():
    tasks = ["A", "B"]
    percentages = [75, 25]
    task_hours, schedule = compute_schedule(tasks, percentages, available_days=2, hours_per_day=8)
    # Totals: 16 hours -> A=12, B=4
    assert [round(x, 2) for x in task_hours] == [12.0, 4.0]
    # Day 1: A gets 8; Day 2: A gets 4 then B gets 4
    assert schedule == [[8.0, 4.0], [0.0, 4.0]]


def test_empty_inputs_return_empty():
    tasks = []
    percentages = []
    task_hours, schedule = compute_schedule(tasks, percentages, available_days=5, hours_per_day=8)
    assert task_hours == []
    assert schedule == []