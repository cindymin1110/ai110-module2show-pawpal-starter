from datetime import date, timedelta
import pytest

from pawpal_system import Owner, Pet, Task, Schedule, Scheduler


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def today():
    return date.today()


@pytest.fixture
def owner(today):
    o = Owner(name="Alex", available_minutes=120)
    biscuit = Pet(name="Biscuit", breed="Golden Retriever")
    mochi = Pet(name="Mochi", breed="Shiba Inu")
    biscuit.add_task(Task("Morning Walk", 30, "high",   time="07:00", frequency="daily",  due_date=today))
    biscuit.add_task(Task("Feeding",      10, "high",   time="08:00", frequency="daily",  due_date=today))
    biscuit.add_task(Task("Grooming",     20, "medium", time="10:00", frequency="weekly", due_date=today))
    mochi.add_task(Task("Enrichment",     15, "low",    time="09:00", frequency="once",   due_date=today))
    o.add_pet(biscuit)
    o.add_pet(mochi)
    return o


# ── Phase 2 tests ─────────────────────────────────────────────────────────────

def test_mark_complete_changes_status(today):
    task = Task("Walk", 20, "high", time="08:00", frequency="once", due_date=today)
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_count():
    pet = Pet(name="Rex", breed="Lab")
    assert len(pet.tasks) == 0
    pet.add_task(Task("Walk", 20, "high"))
    pet.add_task(Task("Feed", 10, "high"))
    assert len(pet.tasks) == 2


# ── Phase 5 tests ─────────────────────────────────────────────────────────────

def test_sort_by_time_returns_chronological_order(owner):
    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_time()
    times = [t.time for t in sorted_tasks]
    assert times == sorted(times)


def test_sort_by_time_handles_out_of_order_input():
    pet = Pet("Dog", "Lab")
    pet.add_task(Task("C", 10, "low",  time="10:00"))
    pet.add_task(Task("A", 10, "low",  time="08:00"))
    pet.add_task(Task("B", 10, "low",  time="09:00"))
    o = Owner("Sam", 120)
    o.add_pet(pet)
    scheduler = Scheduler(o)
    names = [t.name for t in scheduler.sort_by_time()]
    assert names == ["A", "B", "C"]


def test_recurring_daily_creates_next_day_task(today):
    pet = Pet("Biscuit", "Golden Retriever")
    task = Task("Morning Walk", 30, "high", time="07:00", frequency="daily", due_date=today)
    pet.add_task(task)
    o = Owner("Alex", 120)
    o.add_pet(pet)
    scheduler = Scheduler(o)

    scheduler.mark_task_complete(task, pet)

    assert task.completed is True
    assert len(pet.tasks) == 2
    next_task = pet.tasks[1]
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.completed is False
    assert next_task.frequency == "daily"


def test_recurring_weekly_creates_next_week_task(today):
    pet = Pet("Biscuit", "Golden Retriever")
    task = Task("Grooming", 20, "medium", time="10:00", frequency="weekly", due_date=today)
    pet.add_task(task)
    o = Owner("Alex", 120)
    o.add_pet(pet)
    scheduler = Scheduler(o)

    scheduler.mark_task_complete(task, pet)

    next_task = pet.tasks[1]
    assert next_task.due_date == today + timedelta(weeks=1)


def test_once_task_does_not_recur(today):
    pet = Pet("Mochi", "Shiba Inu")
    task = Task("Vet Visit", 60, "high", time="14:00", frequency="once", due_date=today)
    pet.add_task(task)
    o = Owner("Alex", 120)
    o.add_pet(pet)
    scheduler = Scheduler(o)

    scheduler.mark_task_complete(task, pet)

    assert len(pet.tasks) == 1   # no new task added


def test_detect_conflicts_flags_same_time(owner):
    # Add a second task at 07:00 — same as Morning Walk
    mochi = owner.pets[1]
    mochi.add_task(Task("Playtime", 15, "low", time="07:00", due_date=date.today()))

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_conflicts()
    assert len(warnings) == 1
    assert "07:00" in warnings[0]


def test_detect_conflicts_no_warning_when_clear():
    pet = Pet("Rex", "Lab")
    pet.add_task(Task("Walk", 20, "high", time="07:00"))
    pet.add_task(Task("Feed", 10, "high", time="08:00"))
    o = Owner("Sam", 120)
    o.add_pet(pet)
    scheduler = Scheduler(o)
    assert scheduler.detect_conflicts() == []


def test_generate_respects_available_minutes(today):
    pet = Pet("Rex", "Lab")
    for i, t in enumerate(["06:00", "07:00", "08:00", "09:00"]):
        pet.add_task(Task(f"Task{i}", 40, "high", time=t, due_date=today))
    o = Owner("Sam", available_minutes=100)
    o.add_pet(pet)
    scheduler = Scheduler(o)

    schedule = scheduler.generate(today)
    assert schedule.total_time <= 100


def test_filter_by_pet(owner):
    scheduler = Scheduler(owner)
    tasks = scheduler.filter_by_pet("Biscuit")
    assert len(tasks) == 3
    assert all(t.name in {"Morning Walk", "Feeding", "Grooming"} for t in tasks)


def test_filter_by_status_pending(owner):
    scheduler = Scheduler(owner)
    all_tasks = owner.get_all_tasks()
    all_tasks[0].mark_complete()

    pending = scheduler.filter_by_status(completed=False)
    done = scheduler.filter_by_status(completed=True)
    assert len(done) == 1
    assert len(pending) == len(all_tasks) - 1


def test_schedule_add_task_enforces_budget():
    schedule = Schedule(date.today(), max_minutes=30)
    t1 = Task("Walk", 20, "high", time="07:00")
    t2 = Task("Feed", 20, "high", time="08:00")   # would exceed budget

    assert schedule.add_task(t1) is True
    assert schedule.add_task(t2) is False
    assert schedule.total_time == 20
