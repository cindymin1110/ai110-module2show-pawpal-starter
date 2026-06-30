# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My initial UML design included five classes: `Owner`, `Pet`, `Task`, `Schedule`, and `Scheduler`.

- `Owner` stores the pet owner's name and how many minutes they have available in a day.
- `Pet` stores the pet's name and breed, and is linked to its owner via a composition relationship.
- `Task` represents a single care item (such as a walk or feeding) with a name, duration, priority level, and a flag for whether it recurs daily.
- `Schedule` holds the list of tasks planned for a specific date, tracks total time used, and can display the final plan.
- `Scheduler` is responsible for the core logic — it takes an owner, a pet, and a list of tasks, and generates a `Schedule` by filtering tasks based on the owner's available time.

**b. Design changes**

Yes, the design changed significantly during implementation:

- **`Task` gained three new fields:** `time` (HH:MM string for sorting and conflict detection), `frequency` ("once" / "daily" / "weekly" replacing the boolean `is_recurring`), and `due_date` (needed to schedule recurring follow-ups). A `completed` flag and `mark_complete()` method were also added so the task can own its own state transition.
- **`Pet` now holds a list of tasks** (`tasks: list[Task]`). In the initial design, tasks were passed directly to the Scheduler, making it impossible to associate tasks with a specific pet. Embedding them in `Pet` enables per-pet filtering and recurring task scheduling.
- **`Owner` now holds a list of pets** (`pets: list[Pet]`) and has `add_pet()` / `get_all_tasks()` methods. The Scheduler can ask the Owner for all tasks rather than receiving them as a constructor argument.
- **`Scheduler` constructor changed** from `Scheduler(owner, pet, tasks)` to `Scheduler(owner)`. Because the Owner already aggregates all pets and tasks, passing them separately was redundant and would have caused data-sync bugs.
- **`Schedule` gained a `max_minutes` parameter** so `add_task()` can enforce the owner's time budget without needing a reference back to the Owner.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers two hard constraints:

1. **Time budget** — `owner.available_minutes` acts as a daily cap. Tasks are added to the schedule in chronological order until the budget is exhausted; any task that would push the total over the limit is skipped.
2. **Due date** — `Scheduler.generate()` only considers tasks whose `due_date` matches the target date. This prevents past-due or future tasks from cluttering today's schedule.

I chose time as the most important constraint because it is the owner's primary bottleneck: a pet owner can always choose to deprioritize a low-priority task, but they cannot manufacture more time. Priority is surfaced in the display but does not reorder tasks — tasks are sorted by scheduled time, which is more practical for a daily routine.

**b. Tradeoffs**

The conflict detector checks for exact `time` string matches (e.g., both tasks at "10:00"). It does **not** check whether task durations overlap — if Grooming takes 20 minutes starting at 10:00 and Nail Trim starts at 10:15, no conflict is flagged even though they physically overlap. This tradeoff keeps the algorithm simple (O(n) with a hash map) and avoids needing a full interval-overlap check. For a real production app this would be a limitation, but for a daily scheduling assistant where times are entered coarsely (in whole hours or half-hours), exact matches are the most common source of accidental double-booking.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI assistance in three distinct phases, each with a separate chat session to keep context clean:

- **Design phase:** I described the four target classes and asked AI to generate a Mermaid.js UML diagram. The diagram was a useful starting point but missed the `time` attribute on `Task` and the list relationships (Owner→Pet, Pet→Task), which I added manually.
- **Implementation phase:** I asked AI to explain how Python `dataclasses` handle mutable default values, and it introduced me to `field(default_factory=list)`. This was the most directly useful suggestion in the project.
- **Testing phase:** I asked AI "what are the most important edge cases to test for a recurring-task scheduler?" and used its answer as a checklist — it suggested testing "once" tasks, weekly tasks, and empty-pet edge cases that I had not thought of.

The most helpful prompt pattern was attaching the current file and asking a focused question: "Given these skeletons, how should Scheduler retrieve tasks from the Owner?" That approach kept AI responses grounded in my actual code rather than generating abstract examples.

**b. Judgment and verification**

When implementing conflict detection, AI suggested raising a `ValueError` when a conflict was found. I rejected this because the spec explicitly said "returns a warning message rather than crashing the program," and throwing an exception would crash the Streamlit app mid-render. I kept AI's underlying dictionary-scan algorithm but changed the return type from raising an exception to returning a list of warning strings that the UI could display with `st.warning()`.

I verified the change by writing `test_detect_conflicts_flags_same_time`, which confirms the method returns a non-empty list (not an exception) when two tasks share a time slot.

---

## 4. Testing and Verification

**a. What you tested**

The 13-test suite covers:

| Test | Why it matters |
|------|---------------|
| `test_mark_complete_changes_status` | Core state transition — the foundation of recurring logic |
| `test_add_task_increases_pet_count` | Basic data model integrity |
| `test_sort_by_time_returns_chronological_order` | The primary output ordering guarantee |
| `test_sort_by_time_handles_out_of_order_input` | Tasks are rarely entered in order in the UI |
| `test_recurring_daily_creates_next_day_task` | The most complex behavior in the system |
| `test_recurring_weekly_creates_next_week_task` | Variant of the above with different timedelta |
| `test_once_task_does_not_recur` | Edge case: "once" tasks must not spawn infinite copies |
| `test_detect_conflicts_flags_same_time` | Conflict detection happy path |
| `test_detect_conflicts_no_warning_when_clear` | Ensures no false positives |
| `test_generate_respects_available_minutes` | The time-budget constraint is the core scheduling rule |
| `test_filter_by_pet` | Per-pet view is a key UI feature |
| `test_filter_by_status_pending` | Drives the "pending" filter in the Streamlit sidebar |
| `test_schedule_add_task_enforces_budget` | `Schedule.add_task()` must return False, not silently overflow |

**b. Confidence**

⭐⭐⭐⭐ (4/5). All 13 tests pass and cover the core algorithmic behaviors. The main gaps are:

- **Duration-overlap conflicts** are not detected (see Tradeoffs above).
- **UI state persistence** across Streamlit reruns is tested only manually.
- **Weekly recurrence over multiple weeks** is not tested past the first occurrence.

If I had more time, I would add a fuzz test that creates 50 random tasks and confirms `generate()` always stays within the time budget regardless of input order.

---

## 5. Reflection

**a. What went well**

The "CLI-first" workflow worked exactly as intended. By implementing and testing everything in `main.py` and `pytest` before opening `app.py`, I had high confidence in the backend logic before worrying about Streamlit's stateless re-run model. The test suite caught a bug where `filter_by_status()` was accidentally filtering in-place and modifying the original list — something that would have been invisible in the UI.

**b. What you would improve**

The `Scheduler.generate()` method currently skips tasks that would exceed the time budget in sorted-time order, which means a short low-priority task at 14:00 could be excluded while a long high-priority task at 09:00 is kept even if it crowds out more important afternoon work. A better approach would use a priority-queue or knapsack algorithm to optimize total value (priority × duration) within the budget, not just a greedy first-fit.

**c. Key takeaway**

The biggest lesson was that **AI is most useful when it works on a concrete artifact, not an abstract question**. Generic prompts like "how do I build a scheduler?" produced boilerplate that did not fit my design. Prompts like "given this `Scheduler` class, how should `sort_by_time()` handle the HH:MM string format?" produced targeted, immediately usable suggestions. The human role in AI-assisted engineering is not just writing code — it is knowing what specific question to ask and which answer to trust.
