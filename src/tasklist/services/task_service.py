try:
    from tasklist.db.storage import load_task_state, save_task_state
except ModuleNotFoundError:
    from db.storage import load_task_state, save_task_state
from datetime import date


def add_task(title):
    state = load_task_state()
    tasks = state["tasks"]
    tasks.append(
        {
            "title": title,
            "completed": False,
            "created_date": date.today().isoformat(),
        }
    )
    state["tasks"] = tasks
    save_task_state(state)
    return len(tasks)


def list_tasks():
    return load_task_state()["tasks"]


def list_completed_tasks():
    completed_tasks = load_task_state()["completed_tasks"]
    return [task for task in completed_tasks if task.get("completed", False)]


def complete_task(index):
    state = load_task_state()
    tasks = state["tasks"]

    if index < 1 or index > len(tasks):
        raise IndexError("Invalid task number")

    tasks[index - 1]["completed"] = True
    state["tasks"] = tasks
    save_task_state(state)


def delete_task(index):
    state = load_task_state()
    tasks = state["tasks"]

    if index < 1 or index > len(tasks):
        raise IndexError("Invalid task number")

    tasks.pop(index - 1)
    state["tasks"] = tasks
    save_task_state(state)


def move_completed_tasks():
    state = load_task_state()
    tasks = state["tasks"]
    completed_tasks = state["completed_tasks"]

    moved = [task for task in tasks if task.get("completed", False)]
    remaining = [task for task in tasks if not task.get("completed", False)]

    completed_tasks.extend(moved)
    state["tasks"] = remaining
    state["completed_tasks"] = completed_tasks
    save_task_state(state)

    return len(moved)