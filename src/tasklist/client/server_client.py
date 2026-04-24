import json
import urllib.error
import urllib.parse
import urllib.request


class TaskServerError(Exception):
    pass


def _request(server_url, method, path, payload=None):
    base_url = server_url.rstrip("/")
    url = f"{base_url}{path}"
    data = None
    headers = {}

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, data=data, method=method, headers=headers)

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            response_text = response.read().decode("utf-8")
            if not response_text:
                return {}
            return json.loads(response_text)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(body)
            message = payload.get("error") or payload.get("message") or body
        except json.JSONDecodeError:
            message = body or str(exc)
        raise TaskServerError(message) from exc
    except urllib.error.URLError as exc:
        raise TaskServerError(
            f"Could not connect to task server at {server_url}. Start it with 'tasks server'."
        ) from exc


def list_tasks(server_url):
    response = _request(server_url, "GET", "/tasks")
    return response.get("tasks", [])


def add_task(server_url, title):
    response = _request(server_url, "POST", "/tasks", {"title": title})
    return response["id"]


def complete_task(server_url, index):
    _request(server_url, "POST", f"/tasks/{index}/complete")


def delete_task(server_url, index):
    _request(server_url, "DELETE", f"/tasks/{index}")


def list_completed_tasks(server_url):
    response = _request(server_url, "GET", "/tasks/completed")
    return response.get("tasks", [])


def move_completed_tasks(server_url):
    response = _request(server_url, "POST", "/tasks/move-completed")
    return response.get("moved", 0)
