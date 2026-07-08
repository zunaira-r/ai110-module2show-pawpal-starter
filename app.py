from datetime import datetime, time

import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

PRIORITY_MAP = {"low": 1, "medium": 3, "high": 5}

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# --- Session "vault": create the Owner and Scheduler once, then reuse them ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner(ownerID="O1", name="Jordan")
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(ownerID="O1")
if "pet_counter" not in st.session_state:
    st.session_state.pet_counter = 0
if "task_counter" not in st.session_state:
    st.session_state.task_counter = 0

owner = st.session_state.owner
scheduler = st.session_state.scheduler

# --- Owner ---
st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)

# --- Add a Pet -> Owner.addPet() ---
st.subheader("Add a Pet")
col_a, col_b = st.columns(2)
with col_a:
    pet_name = st.text_input("Pet name", value="Mochi")
with col_b:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    st.session_state.pet_counter += 1
    pet = Pet(
        petID=f"P{st.session_state.pet_counter}",
        ownerID=owner.ownerID,
        name=pet_name,
        type=species,
    )
    owner.addPet(pet)
    st.success(f"Added {pet.name} ({pet.type}).")

pets = owner.viewPets()
if pets:
    st.caption("Current pets: " + ", ".join(f"{p.name} ({p.petID})" for p in pets))

# --- Add a Task -> Owner.addTask() ---
st.subheader("Schedule a Task")
if not pets:
    st.info("Add a pet first, then you can schedule tasks for it.")
else:
    pet_by_label = {f"{p.name} ({p.petID})": p.petID for p in pets}
    selected_pet = st.selectbox("For pet", list(pet_by_label.keys()))

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority_label = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    col4, col5 = st.columns(2)
    with col4:
        task_type = st.selectbox("Type", ["walk", "feed", "medication", "appointment"])
    with col5:
        due_time = st.time_input("Due time (today)", value=time(8, 0))

    if st.button("Add task"):
        st.session_state.task_counter += 1
        due_dt = datetime.combine(datetime.now().date(), due_time)
        task = Task(
            taskID=f"T{st.session_state.task_counter}",
            taskName=task_title,
            taskType=task_type,
            petID=pet_by_label[selected_pet],
            dueDate=due_dt,
            duration=int(duration),
            priority=PRIORITY_MAP[priority_label],
        )
        owner.addTask(task, scheduler)
        st.success(f"Scheduled '{task.taskName}' for {selected_pet}.")

# --- Current tasks -> Scheduler.filterTasks() + sort_by_time() ---
tasks = owner.viewTasks(scheduler)
if tasks:
    pet_names = {p.petID: p.name for p in pets}

    st.subheader("Current Tasks")
    fcol1, fcol2 = st.columns(2)
    with fcol1:
        status_filter = st.selectbox(
            "Filter by status", ["all", "pending", "completed", "cancelled"]
        )
    with fcol2:
        pet_filter = st.selectbox("Filter by pet", ["all"] + [p.name for p in pets])

    # Delegate filtering to the Scheduler, then order chronologically.
    filtered = scheduler.filterTasks(
        status=None if status_filter == "all" else status_filter,
        petName=None if pet_filter == "all" else pet_filter,
        pets=pets,
    )
    filtered = sorted(filtered, key=lambda t: (t.time == "", t.time))

    if filtered:
        st.table(
            [
                {
                    "Time": t.dueDate.strftime("%H:%M") if t.dueDate else "—",
                    "Task": t.taskName,
                    "Type": t.taskType,
                    "Pet": pet_names.get(t.petID, t.petID),
                    "Priority": t.priority,
                    "Status": t.status,
                }
                for t in filtered
            ]
        )
        st.caption(f"Showing {len(filtered)} of {len(tasks)} task(s).")
    else:
        st.warning("No tasks match the selected filters.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# --- Build Schedule -> Scheduler.getDailySchedule() + detectConflicts() ---
st.subheader("Build Schedule")
st.caption("Calls your Scheduler to build today's plan, ordered by due time.")

if st.button("Generate schedule"):
    daily = scheduler.getDailySchedule(datetime.now())
    if not daily:
        st.warning("No tasks scheduled for today. Add some tasks above.")
    else:
        pet_names = {p.petID: p.name for p in pets}
        st.markdown(f"### Today's Schedule — {datetime.now():%A, %b %d %Y}")
        st.success(f"Planned {len(daily)} task(s) for today, ordered by due time.")
        st.table(
            [
                {
                    "Time": f"{t.dueDate:%H:%M}",
                    "Task": t.taskName,
                    "Type": t.taskType,
                    "Pet": pet_names.get(t.petID, t.petID),
                    "Priority": f"P{t.priority}",
                }
                for t in daily
            ]
        )

        # Same-slot clashes (lightweight) -> per-warning messages.
        slot_warnings = scheduler.detectTimeConflicts()
        for warning in slot_warnings:
            st.warning(warning)

        # Interval-overlap clashes that also account for duration.
        conflicts = scheduler.detectConflicts()
        if conflicts:
            names = ", ".join(f"{t.taskName} @ {t.dueDate:%H:%M}" for t in conflicts)
            st.error(f"⚠ Overlapping tasks detected: {names}")
        elif not slot_warnings:
            st.success("✅ No scheduling conflicts detected.")
