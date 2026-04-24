import json
from pathlib import Path


DB_FILE = Path("tasks.json")


def set_db_file(path):
    global DB_FILE
    DB_FILE = Path(path)


def _normalize_task_state(payload):
    if isinstance(payload, list):
        # Backward compatibility with the original file format.
        return {"tasks": payload, "completed_tasks": []}

    if not isinstance(payload, dict):
        return {"tasks": [], "completed_tasks": []}

    tasks = payload.get("tasks")
    completed_tasks = payload.get("completed_tasks")

    if not isinstance(tasks, list):
        tasks = []
    if not isinstance(completed_tasks, list):
        completed_tasks = []

    return {"tasks": tasks, "completed_tasks": completed_tasks}


def load_task_state():
    if not DB_FILE.exists():
        return {"tasks": [], "completed_tasks": []}

    payload = json.loads(DB_FILE.read_text(encoding="utf-8"))
    return _normalize_task_state(payload)


def save_task_state(state):
    normalized = _normalize_task_state(state)
    DB_FILE.write_text(json.dumps(normalized, indent=2), encoding="utf-8")


def load_tasks():
    return load_task_state()["tasks"]


def save_tasks(tasks):
    state = load_task_state()
    state["tasks"] = tasks
    save_task_state(state)
