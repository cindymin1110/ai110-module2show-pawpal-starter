from datetime import date

import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("Smart pet care scheduling — sort, filter, detect conflicts, and handle recurring tasks.")

# ── Session state initialisation ─────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="", available_minutes=120)

owner: Owner = st.session_state.owner

# ── Sidebar: owner setup ──────────────────────────────────────────────────────
with st.sidebar:
    st.header("Owner Settings")
    owner.name = st.text_input("Your name", value=owner.name or "Alex")
    owner.available_minutes = st.number_input(
        "Available minutes today", min_value=10, max_value=720, value=owner.available_minutes
    )
    st.divider()

    st.subheader("Add a Pet")
    new_pet_name = st.text_input("Pet name")
    new_pet_breed = st.text_input("Breed")
    if st.button("Add Pet") and new_pet_name:
        existing = [p.name.lower() for p in owner.pets]
        if new_pet_name.lower() not in existing:
            owner.add_pet(Pet(name=new_pet_name, breed=new_pet_breed or "Unknown"))
            st.success(f"Added {new_pet_name}!")
        else:
            st.warning(f"{new_pet_name} is already in your household.")

# ── Pet list ──────────────────────────────────────────────────────────────────
if not owner.pets:
    st.info("No pets yet — add one in the sidebar to get started.")
    st.stop()

st.subheader(f"{owner.name}'s Pets")
pet_names = [p.name for p in owner.pets]
if pet_names:
    cols = st.columns(len(pet_names))
    for col, pet in zip(cols, owner.pets):
        col.metric(pet.name, pet.breed, f"{len(pet.tasks)} task(s)")

st.divider()

# ── Add a task ────────────────────────────────────────────────────────────────
st.subheader("Add a Task")
col1, col2 = st.columns(2)
with col1:
    target_pet = st.selectbox("Assign to pet", pet_names)
    task_name = st.text_input("Task name", value="Morning Walk")
    task_time = st.text_input("Time (HH:MM)", value="08:00")
with col2:
    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    priority = st.selectbox("Priority", ["high", "medium", "low"])
    frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

if st.button("Add Task") and task_name:
    pet_obj = next(p for p in owner.pets if p.name == target_pet)
    pet_obj.add_task(
        Task(
            name=task_name,
            duration=duration,
            priority=priority,
            time=task_time,
            frequency=frequency,
            due_date=date.today(),
        )
    )
    st.success(f"Added '{task_name}' to {target_pet}.")

st.divider()

# ── Schedule generation ───────────────────────────────────────────────────────
st.subheader("Today's Schedule")
scheduler = Scheduler(owner)

# Conflict warnings
conflicts = scheduler.detect_conflicts()
if conflicts:
    for warning in conflicts:
        st.warning(warning)

if st.button("Generate Schedule"):
    schedule = scheduler.generate()
    if not schedule.tasks:
        st.info("No tasks scheduled for today. Add some tasks above.")
    else:
        rows = [
            {
                "Time": t.time,
                "Task": t.name,
                "Pet": next((p.name for p in owner.pets if t in p.tasks), "—"),
                "Duration (min)": t.duration,
                "Priority": t.priority,
                "Frequency": t.frequency,
            }
            for t in schedule.tasks
        ]
        st.table(rows)
        st.success(
            f"Scheduled {len(schedule.tasks)} task(s) — "
            f"{schedule.total_time} / {owner.available_minutes} min used."
        )

st.divider()

# ── Filtered views ────────────────────────────────────────────────────────────
st.subheader("Filter Tasks")
col_a, col_b = st.columns(2)
with col_a:
    filter_pet = st.selectbox("Filter by pet", ["All"] + pet_names, key="filter_pet")
with col_b:
    filter_status = st.selectbox("Filter by status", ["All", "Pending", "Completed"])

all_tasks = owner.get_all_tasks()
if filter_pet != "All":
    all_tasks = scheduler.filter_by_pet(filter_pet)
if filter_status == "Pending":
    all_tasks = scheduler.filter_by_status(False, all_tasks)
elif filter_status == "Completed":
    all_tasks = scheduler.filter_by_status(True, all_tasks)

if all_tasks:
    rows = [
        {
            "Time": t.time,
            "Task": t.name,
            "Duration (min)": t.duration,
            "Priority": t.priority,
            "Frequency": t.frequency,
            "Done": "✓" if t.completed else "",
        }
        for t in scheduler.sort_by_time(all_tasks)
    ]
    st.table(rows)
else:
    st.info("No tasks match the selected filters.")

st.divider()

# ── Mark task complete ────────────────────────────────────────────────────────
st.subheader("Mark a Task Complete")
all_pending = scheduler.filter_by_status(False)
if all_pending:
    task_labels = {f"{t.time} — {t.name}": (t, next(p for p in owner.pets if t in p.tasks))
                   for t in all_pending}
    selected_label = st.selectbox("Select task to complete", list(task_labels.keys()))
    if st.button("Mark Complete"):
        task_to_complete, pet_of_task = task_labels[selected_label]
        scheduler.mark_task_complete(task_to_complete, pet_of_task)
        if task_to_complete.frequency != "once":
            st.success(
                f"'{task_to_complete.name}' marked complete. "
                f"Next {task_to_complete.frequency} occurrence scheduled!"
            )
        else:
            st.success(f"'{task_to_complete.name}' marked complete.")
        st.rerun()
else:
    st.info("All tasks are already complete!")
