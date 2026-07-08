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
    time: str = ""  # "HH:MM" 24-hour, zero-padded (e.g. "08:30")
    duration: int = 0  # minutes
    priority: int = 0
    status: str = "pending"  # pending | completed | cancelled
    recurrence: str = ""  # e.g. "daily", "weekly", "" for one-off

    def __post_init__(self) -> None:
        """Validate the time string right after the dataclass is constructed."""
        if self.time:  # "" means unscheduled, so only check non-empty values
            self._validate_time(self.time)

    @staticmethod
    def _validate_time(value: str) -> None:
        """Raise ValueError unless value is a zero-padded 24-hour "HH:MM" string.

        Zero-padding matters: sort_by_time relies on lexicographic string
        order matching clock order, which only holds when both parts are two
        digits (so "08:30" not "8:30").
        """
        parts = value.split(":")
        if len(parts) != 2 or not all(p.isdigit() and len(p) == 2 for p in parts):
            raise ValueError(
                f"time must be zero-padded 'HH:MM' (e.g. '08:30'), got {value!r}"
            )
        hours, minutes = int(parts[0]), int(parts[1])
        if not (0 <= hours <= 23 and 0 <= minutes <= 59):
            raise ValueError(f"time out of range 00:00–23:59, got {value!r}")

    def modifyTask(self, **changes) -> None:
        """Update this task's details from the given keyword arguments."""
        for key, value in changes.items():
            if not hasattr(self, key):
                raise AttributeError(f"Task has no attribute {key!r}")
            if key == "time" and value:
                self._validate_time(value)
            setattr(self, key, value)

    def cancelTask(self) -> None:
        """Mark this task as cancelled."""
        self.status = "cancelled"

    def markComplete(self) -> None:
        """Mark this task as completed."""
        self.status = "completed"

    def nextOccurrence(self) -> Optional["Task"]:
        """Return a fresh pending Task for the next occurrence, or None.

        Returns None when the task is one-off (recurrence "") or has no
        dueDate to advance from. timedelta is used for the date math so that
        rollovers across months and years are handled correctly (e.g. a daily
        task due Jan 31 correctly rolls to Feb 1).
        """
        if self.recurrence == "daily":
            delta = timedelta(days=1)
        elif self.recurrence == "weekly":
            delta = timedelta(weeks=1)
        else:
            return None

        if self.dueDate is None:
            return None

        next_due = self.dueDate + delta
        base_id = self.taskID.split("@")[0]  # keep the ID stable across recurrences
        return Task(
            taskID=f"{base_id}@{next_due:%Y%m%d}",
            taskName=self.taskName,
            taskType=self.taskType,
            petID=self.petID,
            dueDate=next_due,
            time=self.time,  # same clock time, just a later date
            duration=self.duration,
            priority=self.priority,
            status="pending",
            recurrence=self.recurrence,
        )

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

    def filterTasks(
        self,
        status: Optional[str] = None,
        petName: Optional[str] = None,
        pets: Optional[list[Pet]] = None,
    ) -> list[Task]:
        """Return tasks filtered by completion status and/or pet name.

        Both filters are optional and combine with logical AND: passing neither
        returns every task, while passing both keeps only tasks matching both.
        A new list is returned; ``self.taskList`` is never mutated.

        Args:
            status: Keep tasks whose ``.status`` equals this value
                ("pending", "completed", or "cancelled"). None means "any".
            petName: Keep tasks belonging to the pet with this name. A Task
                only stores ``petID``, so ``pets`` must also be supplied to
                resolve the name to its petID(s). None means "any".
            pets: The Pet objects used to look up petName -> petID. Ignored
                unless ``petName`` is given.

        Returns:
            A new list of matching Task objects (empty if none match).

        Example:
            >>> scheduler.filterTasks(status="pending", petName="Luna", pets=owner.viewPets())
            [Task(taskID='T2', ...)]
        """
        results = self.taskList

        if status is not None:
            results = [t for t in results if t.status == status]

        if petName is not None:
            matching_ids = {p.petID for p in (pets or []) if p.name == petName}
            results = [t for t in results if t.petID in matching_ids]

        return list(results)

    def sort_by_time(self) -> list[Task]:
        """Return this scheduler's tasks sorted chronologically by their HH:MM time.

        The ``key=lambda t: t.time`` argument tells ``sorted`` to compare each
        task's ``time`` string rather than the Task object itself. Because
        "HH:MM" is fixed-width and zero-padded, plain string (lexicographic)
        comparison already matches clock order — no time parsing needed.

        Returns:
            A new list of Task objects in ascending time order; ``self.taskList``
            is left unchanged.

        Example:
            >>> [t.time for t in scheduler.sort_by_time()]
            ['08:30', '09:15', '13:00']
        """
        return sorted(self.taskList, key=lambda t: t.time)

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

    def completeTask(self, taskID: str) -> Optional[Task]:
        """Mark a task complete and auto-schedule its next occurrence if recurring.

        Returns the newly created follow-up Task (already added to the
        schedule), or None if the completed task was one-off.
        """
        task = next((t for t in self.taskList if t.taskID == taskID), None)
        if task is None:
            raise ValueError(f"Task {taskID!r} is not in the schedule")

        task.markComplete()

        follow_up = task.nextOccurrence()
        if follow_up is not None:
            self.addTaskToSchedule(follow_up)
        return follow_up

    def addTaskToSchedule(self, task: Task) -> None:
        """Add a task to the schedule."""
        if any(t.taskID == task.taskID for t in self.taskList):
            raise ValueError(f"Task {task.taskID!r} already in the schedule")
        self.taskList.append(task)

    def removeTaskFromSchedule(self, taskID: str) -> None:
        """Remove a task from the schedule by its ID."""
        self.taskList = [t for t in self.taskList if t.taskID != taskID]

    def detectTimeConflicts(self) -> list[str]:
        """Return warning messages for tasks sharing the same HH:MM time slot.

        A deliberately "lightweight" check: it groups active (non-cancelled)
        tasks by their ``time`` string and flags any slot holding more than one
        task — whether they belong to the same pet or different pets. It never
        raises; an empty list simply means no clashes were found.
        """
        by_time: dict[str, list[Task]] = {}
        for task in self.taskList:
            if task.status == "cancelled" or not task.time:
                continue  # skip cancelled/unscheduled tasks
            by_time.setdefault(task.time, []).append(task)

        warnings: list[str] = []
        for time_slot, clashing in sorted(by_time.items()):
            if len(clashing) > 1:
                same_pet = len({t.petID for t in clashing}) == 1
                scope = "same pet" if same_pet else "different pets"
                names = ", ".join(f"{t.taskName} (pet {t.petID})" for t in clashing)
                warnings.append(
                    f"WARNING: {len(clashing)} tasks at {time_slot} "
                    f"[{scope}] -> {names}"
                )
        return warnings

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
