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

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
==============================================
  Today's Schedule - Tuesday, Jul 07 2026
  Owner: Zunaiira
==============================================
  08:00  P2  Morning walk         Milo (walk)
  12:30  P3  Lunch feeding        Luna (feed)
  18:00  P5  Evening medication   Luna (medication)
  18:30  P2  Evening walk         Milo (walk)
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
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

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
