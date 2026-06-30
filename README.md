# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Sample Output

```
=== Conflict Warnings ===
  ⚠ Conflict at 10:00: 'Grooming' and 'Nail Trim'

Today's Schedule — 2026-06-30
------------------------------------------------
  07:00  [HIGH  ]  Morning Walk — 30 min [daily]
  08:00  [HIGH  ]  Feeding — 10 min [daily]
  09:00  [LOW   ]  Enrichment — 15 min
  10:00  [MEDIUM]  Grooming — 20 min [weekly]
  10:00  [MEDIUM]  Nail Trim — 10 min
------------------------------------------------
Total: 85 / 120 min

=== All Tasks — Sorted by Time ===
  o 07:00  Morning Walk         [high]  (daily)
  o 08:00  Feeding              [high]  (daily)
  o 09:00  Enrichment           [low]  (once)
  o 10:00  Grooming             [medium]  (weekly)
  o 10:00  Nail Trim            [medium]  (once)
  o 14:00  Vet Check-up         [high]  (once)

=== Recurring Task Demo ===
  Before: 'Morning Walk' completed = False, due = 2026-06-30
  After:  'Morning Walk' completed = True
  -> Next occurrence: 'Morning Walk' due on 2026-07-01
```

## Testing PawPal+

```bash
# Run the full test suite:
python -m pytest tests/test_pawpal.py -v
```

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.13.0, pytest-9.1.1
collected 13 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED
tests/test_pawpal.py::test_add_task_increases_pet_count PASSED
tests/test_pawpal.py::test_sort_by_time_returns_chronological_order PASSED
tests/test_pawpal.py::test_sort_by_time_handles_out_of_order_input PASSED
tests/test_pawpal.py::test_recurring_daily_creates_next_day_task PASSED
tests/test_pawpal.py::test_recurring_weekly_creates_next_week_task PASSED
tests/test_pawpal.py::test_once_task_does_not_recur PASSED
tests/test_pawpal.py::test_detect_conflicts_flags_same_time PASSED
tests/test_pawpal.py::test_detect_conflicts_no_warning_when_clear PASSED
tests/test_pawpal.py::test_generate_respects_available_minutes PASSED
tests/test_pawpal.py::test_filter_by_pet PASSED
tests/test_pawpal.py::test_filter_by_status_pending PASSED
tests/test_pawpal.py::test_schedule_add_task_enforces_budget PASSED

============================== 13 passed in 0.07s ==============================
```

**Confidence Level:** ⭐⭐⭐⭐ (4/5)
All core behaviors are tested including happy paths and edge cases. The main gap is UI integration testing, which requires manual verification in the browser.

## Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts by HH:MM string — lexicographic order matches chronological order for 24-hour times |
| Filtering by pet | `Scheduler.filter_by_pet(pet_name)` | Returns all tasks for the named pet |
| Filtering by status | `Scheduler.filter_by_status(completed)` | Returns pending or completed tasks |
| Conflict detection | `Scheduler.detect_conflicts()` | Warns when two tasks share the same HH:MM slot; returns warning strings rather than raising exceptions |
| Recurring tasks | `Scheduler.mark_task_complete()` / `Task.mark_complete()` | Daily tasks reappear the next day; weekly tasks reappear 7 days later using `timedelta` |
| Budget-aware scheduling | `Scheduler.generate()` / `Schedule.add_task()` | Tasks are skipped when adding them would exceed `owner.available_minutes` |

## Demo Walkthrough

1. **Launch the app:** `streamlit run app.py` opens PawPal+ in the browser.
2. **Set up owner:** In the sidebar, enter your name and how many minutes you have available today (e.g., "Alex", 120 min).
3. **Add pets:** Still in the sidebar, add two pets — e.g., "Biscuit" (Golden Retriever) and "Mochi" (Shiba Inu).
4. **Add tasks:** Use the "Add a Task" form to schedule activities: pick a pet, set a name, time (HH:MM), duration, priority, and frequency. Add a couple of tasks at the same time to trigger the conflict warning.
5. **View conflict warnings:** Any time two tasks share the same HH:MM slot, a yellow warning banner appears automatically above the schedule section.
6. **Generate schedule:** Click "Generate Schedule" to see the day's tasks sorted by time, limited to the available minutes. The table shows pet, duration, priority, and frequency.
7. **Filter tasks:** Use the filter dropdowns to narrow the task list by pet or by completion status (pending vs. completed).
8. **Mark complete:** Pick a task from the "Mark a Task Complete" dropdown and click the button. Daily and weekly tasks automatically get a new instance scheduled for the next occurrence.
