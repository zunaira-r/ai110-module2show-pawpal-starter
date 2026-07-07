"""Simple tests for the PawPal+ system."""

import os
import sys

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
