"""Testing ground for the PawPal+ system.

Builds an Owner with two Pets, adds several Tasks at different times,
and prints "Today's Schedule" to the terminal.
"""

from datetime import datetime

from pawpal_system import Owner, Pet, Scheduler, Task


def build_demo():
    """Create an owner, pets, a scheduler, and some tasks. Return them."""
    # --- Owner ---
    owner = Owner(ownerID="O1", name="Zunaiira", contactInfo="zunaiira.r@gmail.com")

    # --- Pets ---
    milo = Pet(petID="P1", ownerID="O1", name="Milo", type="Dog", breed="Beagle", age=3)
    luna = Pet(
        petID="P2",
        ownerID="O1",
        name="Luna",
        type="Cat",
        breed="Siamese",
        age=2,
        healthIssues=["Sensitive stomach"],
        medications=["Probiotic"],
    )
    owner.addPet(milo)
    owner.addPet(luna)

    # --- Scheduler (the "brain") ---
    scheduler = Scheduler(ownerID=owner.ownerID)

    # --- Tasks at different times today ---
    today = datetime.now().replace(second=0, microsecond=0)
    morning = today.replace(hour=8, minute=0)
    noon = today.replace(hour=12, minute=30)
    evening = today.replace(hour=18, minute=0)
    night = today.replace(hour=18, minute=30)

    tasks = [
        Task("T1", "Morning walk", "walk", "P1", dueDate=morning, duration=30, priority=2),
        Task("T2", "Lunch feeding", "feed", "P2", dueDate=noon, duration=15, priority=3),
        Task("T3", "Evening medication", "medication", "P2", dueDate=evening, duration=5, priority=5),
        Task("T4", "Evening walk", "walk", "P1", dueDate=night, duration=30, priority=2),
    ]
    for task in tasks:
        owner.addTask(task, scheduler)

    return owner, scheduler


def print_todays_schedule(owner: Owner, scheduler: Scheduler) -> None:
    """Print today's tasks across all of the owner's pets, ordered by time."""
    today = datetime.now()
    daily = scheduler.getDailySchedule(today)

    # Map pet IDs to names for friendlier output.
    pet_names = {pet.petID: pet.name for pet in owner.viewPets()}

    print("=" * 46)
    print(f"  Today's Schedule - {today.strftime('%A, %b %d %Y')}")
    print(f"  Owner: {owner.name}")
    print("=" * 46)

    if not daily:
        print("  No tasks scheduled for today.")
        return

    for task in daily:
        when = task.dueDate.strftime("%H:%M")
        pet = pet_names.get(task.petID, task.petID)
        print(f"  {when}  P{task.priority}  {task.taskName:<20} {pet} ({task.taskType})")

    conflicts = scheduler.detectConflicts()
    if conflicts:
        print("-" * 46)
        print("  ! Time conflicts detected:")
        for task in conflicts:
            print(f"    - {task.taskName} at {task.dueDate.strftime('%H:%M')}")


def main() -> None:
    owner, scheduler = build_demo()
    print_todays_schedule(owner, scheduler)


if __name__ == "__main__":
    main()
