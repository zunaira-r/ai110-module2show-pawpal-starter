"""PawPal+ — Smart Pet Care Management System.

Implements the four core classes from the UML class diagram in reflection.md:
Pet, Task, Owner, and Scheduler.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class Pet:
    """A pet owned by an Owner."""

    petID: str
    ownerID: str
    name: str
    type: str
    breed: str = ""
    age: int = 0
    weight: float = 0.0
    healthIssues: list[str] = field(default_factory=list)
    medications: list[str] = field(default_factory=list)
    feedingSchedule: str = ""

    def getUpcomingTasks(self, scheduler: "Scheduler") -> list["Task"]:
        """Return the pet's upcoming (pending) tasks, looked up from the scheduler."""
        tasks = scheduler.getTasksForPet(self.petID)
        upcoming = [t for t in tasks if t.status == "pending"]
        upcoming.sort(key=lambda t: (t.dueDate is None, t.dueDate or datetime.max))
        return upcoming

    def viewMedicalHistory(self) -> str:
        """Return a summary of the pet's health issues and medications."""
        issues = ", ".join(self.healthIssues) if self.healthIssues else "None"
        meds = ", ".join(self.medications) if self.medications else "None"
        return (
            f"Medical History for {self.name} ({self.type}):\n"
            f"  Health issues: {issues}\n"
            f"  Medications: {meds}"
        )


@dataclass
class Task:
    """A single pet-care task (feed, walk, medication, appointment)."""

    taskID: str
    taskName: str
    taskType: str
    petID: str
    dueDate: Optional[datetime] = None
    duration: int = 0  # minutes
    priority: int = 0
    status: str = "pending"  # pending | completed | cancelled
    recurrence: str = ""  # e.g. "daily", "weekly", "" for one-off

    def modifyTask(self, **changes) -> None:
        """Update this task's details from the given keyword arguments."""
        for key, value in changes.items():
            if not hasattr(self, key):
                raise AttributeError(f"Task has no attribute {key!r}")
            setattr(self, key, value)

    def cancelTask(self) -> None:
        """Mark this task as cancelled."""
        self.status = "cancelled"

    def markComplete(self) -> None:
        """Mark this task as completed."""
        self.status = "completed"

    def isOverdue(self) -> bool:
        """Return True if the task is past its due date and not completed."""
        if self.dueDate is None or self.status in ("completed", "cancelled"):
            return False
        return datetime.now() > self.dueDate


@dataclass
class Owner:
    """A pet owner who manages pets and tasks."""

    ownerID: str
    name: str
    contactInfo: str = ""
    pets: list[Pet] = field(default_factory=list)

    def viewPets(self) -> list[Pet]:
        """Return the owner's pets."""
        return list(self.pets)

    def viewTasks(self, scheduler: "Scheduler") -> list[Task]:
        """Return all tasks across the owner's pets, looked up from the scheduler."""
        tasks: list[Task] = []
        for pet in self.pets:
            tasks.extend(scheduler.getTasksForPet(pet.petID))
        return tasks

    def addTask(self, task: Task, scheduler: "Scheduler") -> None:
        """Create a new task and register it with the scheduler."""
        if not any(pet.petID == task.petID for pet in self.pets):
            raise ValueError(f"Task references unknown pet {task.petID!r}")
        scheduler.addTaskToSchedule(task)

    def modifyTask(self, task: Task, scheduler: "Scheduler", **changes) -> None:
        """Modify an existing task held by the scheduler."""
        existing = next(
            (t for t in scheduler.taskList if t.taskID == task.taskID), None
        )
        if existing is None:
            raise ValueError(f"Task {task.taskID!r} is not in the schedule")
        existing.modifyTask(**changes)

    def cancelTask(self, taskID: str, scheduler: "Scheduler") -> None:
        """Cancel a task (by ID) held by the scheduler."""
        task = next((t for t in scheduler.taskList if t.taskID == taskID), None)
        if task is None:
            raise ValueError(f"Task {taskID!r} is not in the schedule")
        task.cancelTask()

    def addPet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        if any(p.petID == pet.petID for p in self.pets):
            raise ValueError(f"Pet {pet.petID!r} already added")
        pet.ownerID = self.ownerID
        self.pets.append(pet)

    def removePet(self, petID: str) -> None:
        """Remove a pet by its ID."""
        self.pets = [p for p in self.pets if p.petID != petID]


@dataclass
class Scheduler:
    """Organizes and prioritizes tasks for display as a schedule."""

    ownerID: str
    taskList: list[Task] = field(default_factory=list)
    dateRange: Optional[tuple[datetime, datetime]] = None

    def getTasksForPet(self, petID: str) -> list[Task]:
        """Return all tasks belonging to the given pet (filtered by task.petID)."""
        return [t for t in self.taskList if t.petID == petID]

    def displaySchedule(self) -> None:
        """Print the full schedule, ordered by priority/due date."""
        tasks = self.prioritizeTasks()
        if not tasks:
            print(f"Schedule for owner {self.ownerID}: (no tasks)")
            return
        print(f"Schedule for owner {self.ownerID}:")
        for t in tasks:
            due = t.dueDate.strftime("%Y-%m-%d %H:%M") if t.dueDate else "unscheduled"
            print(
                f"  [{t.status:^9}] {due}  P{t.priority}  "
                f"{t.taskName} ({t.taskType}) — pet {t.petID}"
            )

    def getDailySchedule(self, date: datetime) -> list[Task]:
        """Return tasks scheduled for a given day, ordered by due time."""
        day_tasks = [
            t for t in self.taskList
            if t.dueDate is not None and t.dueDate.date() == date.date()
        ]
        day_tasks.sort(key=lambda t: t.dueDate)
        return day_tasks

    def prioritizeTasks(self) -> list[Task]:
        """Return tasks sorted by priority (highest first), then by due date."""
        return sorted(
            self.taskList,
            key=lambda t: (
                -t.priority,
                t.dueDate is None,
                t.dueDate or datetime.max,
            ),
        )

    def addTaskToSchedule(self, task: Task) -> None:
        """Add a task to the schedule."""
        if any(t.taskID == task.taskID for t in self.taskList):
            raise ValueError(f"Task {task.taskID!r} already in the schedule")
        self.taskList.append(task)

    def removeTaskFromSchedule(self, taskID: str) -> None:
        """Remove a task from the schedule by its ID."""
        self.taskList = [t for t in self.taskList if t.taskID != taskID]

    def detectConflicts(self) -> list[Task]:
        """Return tasks whose [dueDate, dueDate + duration] windows overlap."""
        scheduled = [
            t for t in self.taskList
            if t.dueDate is not None and t.status != "cancelled"
        ]
        scheduled.sort(key=lambda t: t.dueDate)

        conflicting: list[Task] = []
        for i, a in enumerate(scheduled):
            a_end = a.dueDate + timedelta(minutes=a.duration)
            for b in scheduled[i + 1:]:
                if b.dueDate >= a_end:
                    break  # sorted by start; no later task can overlap a
                if a not in conflicting:
                    conflicting.append(a)
                if b not in conflicting:
                    conflicting.append(b)
        return conflicting
