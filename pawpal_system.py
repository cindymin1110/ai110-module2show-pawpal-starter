from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta


@dataclass
class Task:
    name: str
    duration: int          # minutes
    priority: str          # "high" | "medium" | "low"
    time: str = "08:00"   # "HH:MM" — used for sorting and conflict detection
    frequency: str = "once"  # "once" | "daily" | "weekly"
    due_date: date = field(default_factory=date.today)
    completed: bool = False

    def mark_complete(self) -> Task | None:
        """Mark done; return next-occurrence Task for recurring tasks, else None."""
        self.completed = True
        if self.frequency == "daily":
            return Task(
                name=self.name,
                duration=self.duration,
                priority=self.priority,
                time=self.time,
                frequency=self.frequency,
                due_date=self.due_date + timedelta(days=1),
            )
        if self.frequency == "weekly":
            return Task(
                name=self.name,
                duration=self.duration,
                priority=self.priority,
                time=self.time,
                frequency=self.frequency,
                due_date=self.due_date + timedelta(weeks=1),
            )
        return None


@dataclass
class Pet:
    name: str
    breed: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)


@dataclass
class Owner:
    name: str
    available_minutes: int
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's household."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return every task from every pet."""
        return [task for pet in self.pets for task in pet.tasks]


class Schedule:
    def __init__(self, scheduled_date: date, max_minutes: int = 480):
        """Initialize an empty schedule for the given date."""
        self.date = scheduled_date
        self.tasks: list[Task] = []
        self.total_time: int = 0
        self.max_minutes = max_minutes

    def add_task(self, task: Task) -> bool:
        """Add task if time budget allows; return True if added."""
        if self.total_time + task.duration <= self.max_minutes:
            self.tasks.append(task)
            self.total_time += task.duration
            return True
        return False

    def display(self) -> None:
        """Print the schedule to the terminal in a readable format."""
        print(f"\nToday's Schedule — {self.date}")
        print("-" * 48)
        if not self.tasks:
            print("  (no tasks scheduled)")
        for task in self.tasks:
            freq = f" [{task.frequency}]" if task.frequency != "once" else ""
            print(
                f"  {task.time}  [{task.priority.upper():6}]  "
                f"{task.name} — {task.duration} min{freq}"
            )
        print("-" * 48)
        print(f"Total: {self.total_time} / {self.max_minutes} min\n")


class Scheduler:
    def __init__(self, owner: Owner):
        """Initialize with an owner who holds all pets and their tasks."""
        self.owner = owner

    # ── Core schedule generation ──────────────────────────────────────────

    def generate(self, target_date: date | None = None) -> Schedule:
        """Return a time-sorted Schedule for target_date within available minutes."""
        if target_date is None:
            target_date = date.today()
        schedule = Schedule(target_date, self.owner.available_minutes)
        eligible = [
            t for t in self.owner.get_all_tasks()
            if t.due_date == target_date and not t.completed
        ]
        for task in self.sort_by_time(eligible):
            schedule.add_task(task)
        return schedule

    # ── Algorithmic helpers ───────────────────────────────────────────────

    def sort_by_time(self, tasks: list[Task] | None = None) -> list[Task]:
        """Sort tasks chronologically by their HH:MM time attribute."""
        if tasks is None:
            tasks = self.owner.get_all_tasks()
        return sorted(tasks, key=lambda t: t.time)

    def filter_by_pet(self, pet_name: str) -> list[Task]:
        """Return all tasks belonging to the named pet."""
        for pet in self.owner.pets:
            if pet.name.lower() == pet_name.lower():
                return list(pet.tasks)
        return []

    def filter_by_status(self, completed: bool, tasks: list[Task] | None = None) -> list[Task]:
        """Return tasks matching the given completion status."""
        if tasks is None:
            tasks = self.owner.get_all_tasks()
        return [t for t in tasks if t.completed == completed]

    def detect_conflicts(self, tasks: list[Task] | None = None) -> list[str]:
        """Return warning strings for any tasks sharing the same time slot."""
        if tasks is None:
            tasks = self.owner.get_all_tasks()
        seen: dict[str, str] = {}
        warnings: list[str] = []
        for task in tasks:
            if task.time in seen:
                warnings.append(
                    f"⚠ Conflict at {task.time}: '{seen[task.time]}' and '{task.name}'"
                )
            else:
                seen[task.time] = task.name
        return warnings

    def mark_task_complete(self, task: Task, pet: Pet) -> None:
        """Complete a task and schedule the next occurrence for recurring tasks."""
        next_task = task.mark_complete()
        if next_task:
            pet.add_task(next_task)

    # Legacy alias kept for backward compatibility with the original skeleton
    def filter_by_time(self, time_str: str, tasks: list[Task] | None = None) -> list[Task]:
        """Return tasks scheduled at the exact HH:MM time string."""
        if tasks is None:
            tasks = self.owner.get_all_tasks()
        return [t for t in tasks if t.time == time_str]
