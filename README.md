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

## ✨ Features

PawPal+ implements the following algorithms and behaviors:

- **Sorting by time** — `Scheduler.sort_by_time()` orders tasks chronologically by their zero-padded `"HH:MM"` string, and `getDailySchedule()` returns a single day's tasks ordered by due time.
- **Priority ranking** — `Scheduler.prioritizeTasks()` sorts by priority (highest first), then by due date, so the most important tasks surface first.
- **Filtering** — `Scheduler.filterTasks()` filters tasks by completion status, by pet name, or both (logical AND).
- **Conflict warnings** — `Scheduler.detectTimeConflicts()` flags active tasks sharing the same `"HH:MM"` slot; `detectConflicts()` does the heavier interval-overlap check that also accounts for task `duration`.
- **Daily recurrence** — completing a recurring task (`Scheduler.completeTask()` + `Task.nextOccurrence()`) auto-schedules its next `daily`/`weekly` occurrence, handling month/year rollovers.
- **Task lifecycle** — tasks move through `pending → completed / cancelled` via `markComplete()` and `cancelTask()`, with `isOverdue()` reporting past-due pending tasks.
- **Input validation** — `Task._validate_time()` enforces the zero-padded 24-hour `"HH:MM"` format at construction and on edit, which is what makes lexicographic time sorting correct.

## 🧪 Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest
```

The suite (`tests/test_pawpal.py`) covers the most important scheduling behaviors:

- **Task status** — `markComplete()` moves a task from `pending` to `completed`.
- **Task registration** — adding a task through an owner increases that pet's task count in the scheduler.
- **Sorting correctness** — `sort_by_time()` returns tasks in chronological `HH:MM` order and leaves the original list unmutated.
- **Recurrence logic** — completing a `daily` task marks the original complete and auto-schedules a fresh `pending` task for the next day (including month rollovers, e.g. Jan 31 → Feb 1).
- **Conflict detection** — `detectTimeConflicts()` flags two active tasks sharing a time slot and ignores cancelled tasks.

Sample test output:

```
============================= test session starts =============================
platform win32 -- Python 3.14.0, pytest-9.1.1, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: C:\Users\User\CodePath\ai110-module2show-pawpal-starter
collecting ... collected 6 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [ 16%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED   [ 33%]
tests/test_pawpal.py::test_sort_by_time_returns_chronological_order PASSED [ 50%]
tests/test_pawpal.py::test_completing_daily_task_schedules_next_day PASSED [ 66%]
tests/test_pawpal.py::test_detect_time_conflicts_flags_duplicate_times PASSED [ 83%]
tests/test_pawpal.py::test_detect_time_conflicts_ignores_cancelled_tasks PASSED [100%]

============================== 6 passed in 0.02s ==============================
```

## 📐 Smarter Scheduling

PawPal+ adds four scheduling features on top of the basic task list. Each is
documented below with the method that implements it.

| Feature | Method | Summary |
|---------|--------|---------|
| Sorting | `Scheduler.sort_by_time()` | Orders tasks by `"HH:MM"` time |
| Filtering | `Scheduler.filterTasks()` | Filters by status and/or pet name |
| Conflict detection | `Scheduler.detectTimeConflicts()` | Warns on same-time clashes |
| Recurring tasks | `Task.nextOccurrence()` + `Scheduler.completeTask()` | Auto-reschedules daily/weekly tasks |

### Sorting — `Scheduler.sort_by_time()`

Returns tasks ordered chronologically by their `time` attribute. A lambda key
(`key=lambda t: t.time`) sorts on the `"HH:MM"` string directly; because the
format is zero-padded and fixed-width, lexicographic string order already
matches clock order (`"08:30" < "09:15" < "13:00"`), so no time parsing is
needed. Returns a new list without mutating `taskList`.

### Filtering — `Scheduler.filterTasks(status=None, petName=None, pets=None)`

Filters tasks by **completion status**, **pet name**, or both (combined with
logical AND). Since a `Task` stores only `petID`, filtering by `petName`
requires passing the `pets` list so names can be resolved to IDs (matching pet
IDs are collected into a set for fast lookup). Passing no filters returns all
tasks. Input validation on the `time` field lives in `Task._validate_time()`,
enforced at construction (`__post_init__`) and on `modifyTask()`.

### Conflict detection — `Scheduler.detectTimeConflicts()`

A lightweight check that groups active (non-cancelled) tasks by their `"HH:MM"`
slot in a single pass and flags any slot holding more than one task — for the
same pet *or* different pets. It **returns a list of warning strings instead of
raising**, so the program never crashes; an empty list means no conflicts. (The
heavier interval-overlap check that also accounts for `duration` lives in
`Scheduler.detectConflicts()`.)

### Recurring tasks — `Task.nextOccurrence()` + `Scheduler.completeTask()`

When a `"daily"` or `"weekly"` task is completed via `Scheduler.completeTask()`,
the next occurrence is created and added to the schedule automatically. The date
math lives in `Task.nextOccurrence()`, which uses `timedelta(days=1)` /
`timedelta(weeks=1)` so month/year rollovers are handled correctly (e.g. a daily
task due Jan 31 rolls to Feb 1). One-off tasks (`recurrence=""`) return `None`
and nothing is rescheduled.

## 🎬 Demo Walkthrough

### The UI (Streamlit — `streamlit run app.py`)

The app is a single page with four sections. A user can:

1. **Owner** — set the owner's name.
2. **Add a Pet** — enter a pet name and species and click **Add pet**. Added pets appear in a running caption.
3. **Schedule a Task** — pick a pet, then set a title, duration, priority (low/medium/high), type (walk/feed/medication/appointment), and a due time, then click **Add task**.
4. **Current Tasks** — a live table of all tasks with **filter dropdowns** for status and pet (backed by `Scheduler.filterTasks()`), shown in chronological order.
5. **Build Schedule** — click **Generate schedule** to render today's plan as a table, with conflict banners driven by the Scheduler.

### Example workflow

> Add a pet (**Milo the dog**) → schedule a task (**Morning walk at 08:00**) → schedule another (**Breakfast at 08:00** for **Luna**) → click **Generate schedule** → see today's plan sorted by time, with an `st.warning` flagging the 08:00 clash.

### Key Scheduler behaviors shown

- **Sorting** — tasks entered out of order come back ordered by time (`08:00 → 18:30`).
- **Filtering** — narrowing to `status = pending` or `pet = Luna` updates the table instantly.
- **Conflict warnings** — two tasks at `08:00` trigger both the lightweight same-slot warning (`detectTimeConflicts`) and, since their windows overlap, the interval-overlap error (`detectConflicts`).

### Sample CLI output (`python main.py`)

`main.py` builds an owner (Zunaiira) with two pets (Milo, Luna) and five tasks — deliberately added out of order, with two at 08:00 to force a conflict — then prints the schedule and demonstrates each algorithm:

```
==============================================
  Today's Schedule - Tuesday, Jul 07 2026
  Owner: Zunaiira
==============================================
  08:00  P2  Morning walk         Milo (walk)
  08:00  P3  Breakfast            Luna (feed)
  12:30  P3  Lunch feeding        Luna (feed)
  18:00  P5  Evening medication   Luna (medication)
  18:30  P2  Evening walk         Milo (walk)
----------------------------------------------
  ! Time conflicts detected:
    - Morning walk at 08:00
    - Breakfast at 08:00

==============================================
  Tasks sorted by time (sort_by_time)
==============================================
  08:00  Morning walk         Milo [pending]
  08:00  Breakfast            Luna [pending]
  12:30  Lunch feeding        Luna [pending]
  18:00  Evening medication   Luna [completed]
  18:30  Evening walk         Milo [pending]

==============================================
  Filter: status == 'pending'
==============================================
  08:00  Morning walk         Milo [pending]
  18:30  Evening walk         Milo [pending]
  12:30  Lunch feeding        Luna [pending]
  08:00  Breakfast            Luna [pending]

==============================================
  Filter: petName == 'Luna'
==============================================
  18:00  Evening medication   Luna [completed]
  12:30  Lunch feeding        Luna [pending]
  08:00  Breakfast            Luna [pending]

==============================================
  Time conflict check (detectTimeConflicts)
==============================================
  WARNING: 2 tasks at 08:00 [different pets] -> Morning walk (pet P1), Breakfast (pet P2)
```
