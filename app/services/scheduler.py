def compute_schedule(tasks, percentages, available_days=5, hours_per_day=8):
    """
    Compute schedule without printing. Returns (task_hours, schedule_matrix).
    schedule_matrix is a list of lists: schedule[task_index][day_index].
    """
    # --- Calculate total hours ---
    total_hours = available_days * hours_per_day
    task_hours = [(total_hours * p / 100) for p in percentages]

    # --- Schedule assignment ---
    schedule = [[0.0 for _ in range(available_days)] for _ in tasks]

    current_task = 0
    hours_left = task_hours[current_task] if tasks else 0

    for day in range(available_days):
        space_left = hours_per_day
        while space_left > 0 and current_task < len(tasks):
            assign = min(space_left, hours_left)
            schedule[current_task][day] += assign
            hours_left -= assign
            space_left -= assign
            if hours_left <= 0.0001:  # move to next task
                current_task += 1
                if current_task < len(tasks):
                    hours_left = task_hours[current_task]

    return task_hours, schedule
