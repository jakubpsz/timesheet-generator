"""
Routes for the main blueprint.
Prepares view data so templates do not rely on Python builtins (like zip/range).
"""
from __future__ import annotations

from flask import current_app, render_template, request
from . import bp
from ..services.scheduler import compute_schedule


def _parse_form(form) -> tuple[list[str], list[float], int, int, list[str]]:
    """Parse and validate the incoming form.
    Returns (tasks, percentages, available_days, hours_per_day, errors).
    """
    errors: list[str] = []

    # Maintain original field names to stay compatible with existing HTML
    raw_tasks = form.getlist("tasks[]")
    raw_percents = form.getlist("percentages[]")

    tasks: list[str] = []
    percentages: list[float] = []

    for i, t in enumerate(raw_tasks):
        t = (t or "").strip()
        if not t:
            continue
        tasks.append(t)
        try:
            pct_val = float(raw_percents[i])
        except (ValueError, IndexError):
            errors.append(f"Invalid percentage for task #{i+1}.")
            pct_val = 0.0
        percentages.append(pct_val)

    # Defaults come from config.ini (or env)
    available_days = int(form.get("available_days", current_app.config.get("AVAILABLE_DAYS", 5)))
    hours_per_day = int(form.get("hours_per_day", current_app.config.get("HOURS_PER_DAY", 8)))

    # Validations
    if len(tasks) != len(percentages):
        errors.append("Each task must have a matching percentage.")

    total = sum(percentages)
    if abs(total - 100.0) > 1e-6:
        errors.append("Percentages must sum to 100.")

    if available_days <= 0:
        errors.append("Available days must be a positive integer.")
    if hours_per_day <= 0:
        errors.append("Hours per day must be a positive integer.")

    return tasks, percentages, available_days, hours_per_day, errors


@bp.route("/", methods=["GET", "POST"]
)
def index():
    """Home page with the schedule form and results."""
    result = None
    errors: list[str] = []

    defaults = {
        "available_days": current_app.config.get("AVAILABLE_DAYS", 5),
        "hours_per_day": current_app.config.get("HOURS_PER_DAY", 8),
    }
    # Pre-populate form rows; will be overridden on POST with submitted values
    form_rows: list[dict[str, str]] = [{"task": "", "pct": ""}]

    if request.method == "POST":
        # Preserve raw inputs to repopulate the form after submission
        raw_tasks = request.form.getlist("tasks[]")
        raw_percents = request.form.getlist("percentages[]")

        n = max(len(raw_tasks), len(raw_percents))
        form_rows = [
            {
                "task": (raw_tasks[i] if i < len(raw_tasks) else "").strip(),
                "pct": (raw_percents[i] if i < len(raw_percents) else ""),
            }
            for i in range(n)
        ] or [{"task": "", "pct": ""}]

        # Reflect submitted numeric fields back into the form (even if validation fails)
        submitted_days = request.form.get("available_days")
        submitted_hpd = request.form.get("hours_per_day")
        if submitted_days:
            defaults["available_days"] = submitted_days
        if submitted_hpd:
            defaults["hours_per_day"] = submitted_hpd

        # Parse and compute result for rendering
        tasks, percentages, available_days, hours_per_day, errors = _parse_form(request.form)
        if not errors:
            task_hours, schedule = compute_schedule(tasks, percentages, available_days, hours_per_day)

            # Prepare days and rows for the template to avoid using zip/range in Jinja.
            days = list(range(1, available_days + 1))
            rows = [
                {"task": t, "cells": row, "total": th}
                for t, row, th in zip(tasks, schedule, task_hours)
            ]

            result = {
                "days": days,                   # [1, 2, ..., available_days]
                "rows": rows,                   # list of {task, cells: [h...], total}
                "tasks": tasks,
                "available_days": available_days,
                "hours_per_day": hours_per_day,
            }

    return render_template("index.html", defaults=defaults, errors=errors, result=result, form_rows=form_rows)
