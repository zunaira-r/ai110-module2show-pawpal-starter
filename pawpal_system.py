"""PawPal+ — Smart Pet Care Management System.

Class skeletons generated from the UML class diagram in reflection.md.
Method bodies are left as stubs (``pass`` / ``raise NotImplementedError``)
to be implemented later.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
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

    def getUpcomingTasks(self) -> list["Task"]:
        """Return the pet's upcoming (pending) tasks."""
        raise NotImplementedError

    def viewMedicalHistory(self) -> str:
        """Return a summary of the pet's health issues and medications."""
        raise NotImplementedError


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

    def modifyTask(self) -> None:
        """Update this task's details."""
        raise NotImplementedError

    def cancelTask(self) -> None:
        """Mark this task as cancelled."""
        raise NotImplementedError

    def markComplete(self) -> None:
        """Mark this task as completed."""
        raise NotImplementedError

    def isOverdue(self) -> bool:
        """Return True if the task is past its due date and not completed."""
        raise NotImplementedError


@dataclass
class Owner:
    """A pet owner who manages pets and tasks."""

    ownerID: str
    name: str
    contactInfo: str = ""
    pets: list[Pet] = field(default_factory=list)

    def viewPets(self) -> list[Pet]:
        """Return the owner's pets."""
        raise NotImplementedError

    def viewTasks(self) -> list[Task]:
        """Return all tasks across the owner's pets."""
        raise NotImplementedError

    def addTask(self, task: Task) -> None:
        """Add a new task."""
        raise NotImplementedError

    def modifyTask(self, task: Task) -> None:
        """Modify an existing task."""
        raise NotImplementedError

    def cancelTask(self, taskID: str) -> None:
        """Cancel a task by its ID."""
        raise NotImplementedError

    def addPet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        raise NotImplementedError

    def removePet(self, petID: str) -> None:
        """Remove a pet by its ID."""
        raise NotImplementedError


@dataclass
class Scheduler:
    """Organizes and prioritizes tasks for display as a schedule."""

    ownerID: str
    petID: str = ""
    taskList: list[Task] = field(default_factory=list)
    dateRange: Optional[tuple[datetime, datetime]] = None

    def displaySchedule(self) -> None:
        """Print/return the full schedule."""
        raise NotImplementedError

    def getDailySchedule(self, date: datetime) -> list[Task]:
        """Return tasks scheduled for a given day."""
        raise NotImplementedError

    def prioritizeTasks(self) -> list[Task]:
        """Return tasks sorted by priority/due date."""
        raise NotImplementedError

    def addTaskToSchedule(self, task: Task) -> None:
        """Add a task to the schedule."""
        raise NotImplementedError

    def removeTaskFromSchedule(self, taskID: str) -> None:
        """Remove a task from the schedule by its ID."""
        raise NotImplementedError

    def detectConflicts(self) -> list[Task]:
        """Return tasks that overlap in time."""
        raise NotImplementedError
