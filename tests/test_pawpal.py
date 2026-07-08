"""Simple tests for the PawPal+ system."""

import os
import sys
from datetime import datetime, timedelta

# Allow importing pawpal_system.py from the parent directory.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status():
    """Calling markComplete() should set the task's status to 'completed'."""
    task = Task("T1", "Morning walk", "walk", "P1")
    assert task.status == "pending"

    task.markComplete()

    assert task.status == "completed"


def test_adding_task_increases_pet_task_count():
    """Adding a task for a pet should increase that pet's task count."""
    owner = Owner(ownerID="O1", name="Zunaiira")
    pet = Pet(petID="P1", ownerID="O1", name="Milo", type="Dog")
    owner.addPet(pet)
    scheduler = Scheduler(ownerID="O1")

    before = len(scheduler.getTasksForPet(pet.petID))

    task = Task("T1", "Morning walk", "walk", pet.petID)
    owner.addTask(task, scheduler)

    after = len(scheduler.getTasksForPet(pet.petID))
    assert after == before + 1


def test_sort_by_time_returns_chronological_order():
    """sort_by_time() should return tasks ordered by their HH:MM time."""
    scheduler = Scheduler(ownerID="O1")
    scheduler.addTaskToSchedule(Task("T1", "Lunch", "feed", "P1", time="13:00"))
    scheduler.addTaskToSchedule(Task("T2", "Breakfast", "feed", "P1", time="08:30"))
    scheduler.addTaskToSchedule(Task("T3", "Walk", "walk", "P1", time="09:15"))

    ordered = scheduler.sort_by_time()

    assert [t.time for t in ordered] == ["08:30", "09:15", "13:00"]
    # The original list must not be mutated.
    assert [t.taskID for t in scheduler.taskList] == ["T1", "T2", "T3"]


def test_completing_daily_task_schedules_next_day():
    """Completing a daily recurring task should create one for the following day."""
    due = datetime(2026, 1, 31, 8, 30)
    scheduler = Scheduler(ownerID="O1")
    scheduler.addTaskToSchedule(
        Task("T1", "Morning meds", "medication", "P1",
             dueDate=due, time="08:30", recurrence="daily")
    )

    follow_up = scheduler.completeTask("T1")

    # The original task is now completed.
    original = next(t for t in scheduler.taskList if t.taskID == "T1")
    assert original.status == "completed"

    # A fresh pending task exists for the next day (rolling Jan 31 -> Feb 1).
    assert follow_up is not None
    assert follow_up.status == "pending"
    assert follow_up.dueDate == due + timedelta(days=1)
    assert follow_up.dueDate == datetime(2026, 2, 1, 8, 30)
    assert follow_up.time == "08:30"
    # And it was added to the schedule.
    assert follow_up in scheduler.taskList


def test_detect_time_conflicts_flags_duplicate_times():
    """detectTimeConflicts() should flag two active tasks sharing a time slot."""
    scheduler = Scheduler(ownerID="O1")
    scheduler.addTaskToSchedule(Task("T1", "Walk", "walk", "P1", time="08:30"))
    scheduler.addTaskToSchedule(Task("T2", "Feed", "feed", "P2", time="08:30"))
    scheduler.addTaskToSchedule(Task("T3", "Vet", "appointment", "P1", time="10:00"))

    warnings = scheduler.detectTimeConflicts()

    assert len(warnings) == 1
    assert "08:30" in warnings[0]
    assert "10:00" not in warnings[0]


def test_detect_time_conflicts_ignores_cancelled_tasks():
    """A cancelled task should not count toward a time-slot clash."""
    scheduler = Scheduler(ownerID="O1")
    scheduler.addTaskToSchedule(Task("T1", "Walk", "walk", "P1", time="08:30"))
    cancelled = Task("T2", "Feed", "feed", "P2", time="08:30")
    cancelled.cancelTask()
    scheduler.addTaskToSchedule(cancelled)

    assert scheduler.detectTimeConflicts() == []
