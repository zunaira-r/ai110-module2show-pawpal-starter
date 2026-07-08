# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
three core actions the user should be able to perform: add a pet-related task (walk/feed), view schedule each day, add pet(s)
- What classes did you include, and what responsibilities did you assign to each?
The classes I want to include are: Pet, Owner, Task, Scheduler.

Pet
- Attributes: petID, ownerID, name, type (animal), breed, age, weight, healthIssues, medications, feedingSchedule/dietaryNeeds
- Methods: getUpcomingTasks(), viewMedicalHistory()

Owner
- Attributes: ownerID, name, contactInfo (email/phone), pets (list of Pet)
- Methods: viewPets(), viewTasks(), addTask(), modifyTask(), cancelTask(), addPet(), removePet()

Task
- Attributes: taskID, taskName, taskType (feed/walk/medication/appointment), petID, dueDate/time, duration, priority, status (pending/completed/cancelled), recurrence
- Methods: modifyTask(), cancelTask(), markComplete(), isOverdue()

Scheduler
- Attributes: taskList (list of Task), ownerID, petID, date/dateRange
- Methods: displaySchedule(), getDailySchedule(), prioritizeTasks(), addTaskToSchedule(), removeTaskFromSchedule(), detectConflicts()

Design notes:
- Classes are linked by IDs (ownerID, petID, taskID) rather than names, since names are not unique and can change.
- Relationships are held explicitly: Owner has a list of Pets, and Scheduler holds a list of Tasks.

**Class diagram (Mermaid):**

```classDiagram
    class Pet {
        +String petID
        +String ownerID
        +String name
        +String type
        +String breed
        +int age
        +float weight
        +String[] healthIssues
        +String[] medications
        +String feedingSchedule
        +getUpcomingTasks(Scheduler) Task[]
        +viewMedicalHistory() String
    }

    class Owner {
        +String ownerID
        +String name
        +String contactInfo
        +Pet[] pets
        +viewPets() Pet[]
        +viewTasks(Scheduler) Task[]
        +addTask(Task, Scheduler) void
        +modifyTask(Task, Scheduler) void
        +cancelTask(taskID, Scheduler) void
        +addPet(Pet) void
        +removePet(petID) void
    }

    class Task {
        +String taskID
        +String taskName
        +String taskType
        +String petID
        +DateTime dueDate
        +String time
        +int duration
        +int priority
        +String status
        +String recurrence
        +modifyTask() void
        +cancelTask() void
        +markComplete() void
        +isOverdue() bool
        +nextOccurrence() Task
        -validate_time(value) void
    }

    class Scheduler {
        +String ownerID
        +Task[] taskList
        +DateRange dateRange
        +getTasksForPet(petID) Task[]
        +displaySchedule() void
        +getDailySchedule(date) Task[]
        +filterTasks(status, petName, pets) Task[]
        +sort_by_time() Task[]
        +prioritizeTasks() Task[]
        +completeTask(taskID) Task
        +addTaskToSchedule(Task) void
        +removeTaskFromSchedule(taskID) void
        +detectTimeConflicts() String[]
        +detectConflicts() Task[]
    }

    Owner "1" o-- "0..*" Pet : owns
    Scheduler "1" *-- "0..*" Task : owns all tasks
    Owner "1" ..> "1" Scheduler : delegates task CRUD
    Pet "1" ..> "1" Scheduler : looks up its tasks
    Task ..> Pet : references by petID

```


**b. Design changes**

- Did your design change during implementation?

    Yes. During implementation I fixed the issue of where tasks should live to one location so its updated everywhere automatically. 
#- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

sort_by_time() orders tasks by their "HH:MM" time, and getDailySchedule() filters to a single day. Time is the backbone of a daily care routine.

- How did you decide which constraints mattered most?
I chose the ranking as time first and then priority. Its because the owner should know what happens at a certain time and if there is only the opportunity to do certain tasks and not all, thats when priority comes in.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
 My lightweight detectTimeConflicts() matches conflicts by exact "HH:MM" string equality, not by true time-window overlap. An 08:00 task lasting 30 minutes and an 08:15 task would not be flagged, even though they actually overlap. (My heavier detectConflicts() does the real interval math using duration, but the lightweight one intentionally does not.)

- Why is that tradeoff reasonable for this scenario?
tasks are short and set at clean times like 08:00 or 12:30, so exact-slot matching catches the conflicts that actually happen. In return, I get a fast check that prints a warning instead of crashing
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used it to brainstorm and refactor my ideas as well as cross check if my ideas stayed aligned to the goal throughout the project.
- What kinds of prompts or questions were most helpful?
The prompts most helpful were ones where I was more specific, descriptive and being clear with my ideas

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
When it asked to change the detectTimeConflict() methods, it was giving different opinioms

- How did you evaluate or verify what the AI suggested?
I had to ask it various follow up questions, drawbacks of each idea it suggested and then chose one that seemed most fitting

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

I wrote six tests in `tests/test_pawpal.py` covering the behaviors most central to the app:
1. **Task status change** — `markComplete()` moves a task from `pending` to `completed`.
2. **Task registration** — adding a task through `Owner.addTask()` actually increases that pet's task count in the Scheduler (confirms tasks live in one place and the Owner→Scheduler wiring works).
3. **Sorting correctness** — `sort_by_time()` returns tasks in chronological `HH:MM` order and does *not* mutate the original `taskList`.
4. **Recurrence logic** — completing a `daily` task marks the original complete and auto-creates a fresh `pending` task for the next day, including the month rollover Jan 31 → Feb 1.
5. **Conflict detection** — `detectTimeConflicts()` flags two active tasks sharing a time slot and names that slot.
6. **Conflict edge case** — a *cancelled* task at the same time does not trigger a false conflict.

- Why were these tests important?

These are the behaviors the whole scheduler is built on. Sorting is the backbone of the daily plan, recurrence is the trickiest logic, and conflict detection is the feature most likely to mislead an owner if it were wrong.

**b. Confidence**

- How confident are you that your scheduler works correctly?

I am fairly confident for the core paths. All six tests pass, and they cover the happy path plus two edge cases (month rollover, cancelled-task exclusion). My confidence is lower on the areas I haven't tested yet.

- What edge cases would you test next if you had more time?

  - `Task._validate_time()` rejecting bad input (`"8:30"`, `"25:00"`, `"12:60"`), including via `modifyTask()`.
  - `filterTasks()` combining status **and** petName, and the `petName` lookup when no `pets` list is supplied.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
The way the classes interact with eachother.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I might've redesigned the UML to be cleaner

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
I learned how to control the work while using an agent. I learned how easily a project can get out of hand if AI keeps making the decisions but also learnt the technique to stoll remain in control as the architect and prevent this from happening
