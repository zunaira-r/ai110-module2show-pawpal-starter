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

    # Added deliberately OUT OF ORDER so sort_by_time() has real work to do.
    tasks = [
        Task("T3", "Evening medication", "medication", "P2", dueDate=evening,
             time="18:00", duration=5, priority=5, status="completed"),
        Task("T1", "Morning walk", "walk", "P1", dueDate=morning,
             time="08:00", duration=30, priority=2),
        Task("T4", "Evening walk", "walk", "P1", dueDate=night,
             time="18:30", duration=30, priority=2),
        Task("T2", "Lunch feeding", "feed", "P2", dueDate=noon,
             time="12:30", duration=15, priority=3),
        # T5 deliberately clashes with T1 (both at 08:00) to trigger a warning.
        Task("T5", "Breakfast", "feed", "P2", dueDate=morning,
             time="08:00", duration=10, priority=3),
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


def print_sorted_and_filtered(owner: Owner, scheduler: Scheduler) -> None:
    """Demonstrate the Scheduler.sort_by_time() and filterTasks() methods."""
    pet_names = {pet.petID: pet.name for pet in owner.viewPets()}

    def show(task: Task) -> str:
        pet = pet_names.get(task.petID, task.petID)
        return f"{task.time}  {task.taskName:<20} {pet} [{task.status}]"

    # --- sort_by_time(): tasks were added out of order; show them ordered ---
    print("\n" + "=" * 46)
    print("  Tasks sorted by time (sort_by_time)")
    print("=" * 46)
    for task in scheduler.sort_by_time():
        print(f"  {show(task)}")

    # --- filterTasks(status=...): only pending tasks ---
    print("\n" + "=" * 46)
    print("  Filter: status == 'pending'")
    print("=" * 46)
    for task in scheduler.filterTasks(status="pending"):
        print(f"  {show(task)}")

    # --- filterTasks(petName=...): only Luna's tasks ---
    print("\n" + "=" * 46)
    print("  Filter: petName == 'Luna'")
    print("=" * 46)
    for task in scheduler.filterTasks(petName="Luna", pets=owner.viewPets()):
        print(f"  {show(task)}")


def print_time_conflicts(scheduler: Scheduler) -> None:
    """Print any same-time-slot warnings from the lightweight conflict check."""
    print("\n" + "=" * 46)
    print("  Time conflict check (detectTimeConflicts)")
    print("=" * 46)

    warnings = scheduler.detectTimeConflicts()
    if not warnings:
        print("  No time conflicts found.")
        return
    for warning in warnings:
        print(f"  {warning}")


def main() -> None:
    owner, scheduler = build_demo()
    print_todays_schedule(owner, scheduler)
    print_sorted_and_filtered(owner, scheduler)
    print_time_conflicts(scheduler)


if __name__ == "__main__":
    main()
