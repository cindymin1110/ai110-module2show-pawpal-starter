from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

# ── Setup: owner and two pets ─────────────────────────────────────────────────
owner = Owner(name="Alex", available_minutes=120)

biscuit = Pet(name="Biscuit", breed="Golden Retriever")
mochi = Pet(name="Mochi", breed="Shiba Inu")
owner.add_pet(biscuit)
owner.add_pet(mochi)

today = date.today()

# ── Add tasks (out of time order to demonstrate sorting) ─────────────────────
biscuit.add_task(Task("Feeding",       duration=10, priority="high",   time="08:00", frequency="daily",  due_date=today))
biscuit.add_task(Task("Morning Walk",  duration=30, priority="high",   time="07:00", frequency="daily",  due_date=today))
biscuit.add_task(Task("Grooming",      duration=20, priority="medium", time="10:00", frequency="weekly", due_date=today))

mochi.add_task(Task("Enrichment",      duration=15, priority="low",    time="09:00", frequency="once",   due_date=today))
mochi.add_task(Task("Vet Check-up",    duration=45, priority="high",   time="14:00", frequency="once",   due_date=today))
# Intentional conflict — same time as Biscuit's Grooming
mochi.add_task(Task("Nail Trim",       duration=10, priority="medium", time="10:00", frequency="once",   due_date=today))

scheduler = Scheduler(owner)

# ── 1. Conflict detection ─────────────────────────────────────────────────────
print("=== Conflict Warnings ===")
conflicts = scheduler.detect_conflicts()
if conflicts:
    for warning in conflicts:
        print(f"  {warning}")
else:
    print("  No conflicts detected.")

# ── 2. Today's schedule (sorted, time-budget respected) ──────────────────────
schedule = scheduler.generate()
schedule.display()

# ── 3. All tasks sorted by time ───────────────────────────────────────────────
print("=== All Tasks — Sorted by Time ===")
for t in scheduler.sort_by_time():
    status = "✓" if t.completed else "○"
    print(f"  {status} {t.time}  {t.name:<20} [{t.priority}]  ({t.frequency})")

# ── 4. Filter by pet ──────────────────────────────────────────────────────────
print("\n=== Biscuit's Tasks Only ===")
for t in scheduler.filter_by_pet("Biscuit"):
    print(f"  {t.name}")

# ── 5. Recurring task demo ────────────────────────────────────────────────────
print("\n=== Recurring Task Demo ===")
morning_walk = biscuit.tasks[1]   # the Morning Walk added second
print(f"  Before: '{morning_walk.name}' completed = {morning_walk.completed}, due = {morning_walk.due_date}")
scheduler.mark_task_complete(morning_walk, biscuit)
print(f"  After:  '{morning_walk.name}' completed = {morning_walk.completed}")
new_tasks = [t for t in biscuit.tasks if not t.completed and t.name == "Morning Walk"]
if new_tasks:
    print(f"  ↳ Next occurrence: '{new_tasks[0].name}' due on {new_tasks[0].due_date}")
