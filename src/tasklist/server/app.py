import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

try:
    from tasklist.db.storage import set_db_file
    from tasklist.services.task_service import (
        add_task,
        complete_task,
        delete_task,
        list_completed_tasks,
        list_tasks,
        move_completed_tasks,
    )
except ModuleNotFoundError:
    from db.storage import set_db_file  # type: ignore[import-not-found]
    from services.task_service import (  # type: ignore[import-not-found]
        add_task,
        complete_task,
        delete_task,
        list_completed_tasks,
        list_tasks,
        move_completed_tasks,
    )


class TaskRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length == 0:
            return {}
        raw = self.rfile.read(content_length).decode("utf-8")
        if not raw.strip():
            return {}
        return json.loads(raw)

    def do_GET(self):
        if self.path == "/health":
            self._send_json(200, {"status": "ok"})
            return

        if self.path == "/tasks":
            self._send_json(200, {"tasks": list_tasks()})
            return

        if self.path == "/tasks/completed":
            self._send_json(200, {"tasks": list_completed_tasks()})
            return

        self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path == "/tasks":
            try:
                payload = self._read_json()
            except json.JSONDecodeError:
                self._send_json(400, {"error": "Invalid JSON body"})
                return

            title = str(payload.get("title", "")).strip()
            if not title:
                self._send_json(400, {"error": "Task title is required"})
                return

            task_id = add_task(title)
            self._send_json(201, {"id": task_id, "title": title})
            return

        if self.path.startswith("/tasks/") and self.path.endswith("/complete"):
            index_part = self.path[len("/tasks/") : -len("/complete")]
            try:
                index = int(index_part.strip("/"))
            except ValueError:
                self._send_json(400, {"error": "Invalid task number"})
                return

            try:
                complete_task(index)
            except IndexError as exc:
                self._send_json(404, {"error": str(exc)})
                return

            self._send_json(200, {"status": "ok"})
            return

        if self.path == "/tasks/move-completed":
            moved_count = move_completed_tasks()
            self._send_json(200, {"moved": moved_count})
            return

        self._send_json(404, {"error": "Not found"})

    def do_DELETE(self):
        if self.path.startswith("/tasks/"):
            index_part = self.path[len("/tasks/") :]
            try:
                index = int(index_part.strip("/"))
            except ValueError:
                self._send_json(400, {"error": "Invalid task number"})
                return

            try:
                delete_task(index)
            except IndexError as exc:
                self._send_json(404, {"error": str(exc)})
                return

            self._send_json(200, {"status": "ok"})
            return

        self._send_json(404, {"error": "Not found"})

    def log_message(self, _format, *_args):
        # Keep CLI output clean while the server is running.
        return


def run_server(host, port, data_file):
    set_db_file(data_file)
    server = ThreadingHTTPServer((host, port), TaskRequestHandler)
    print(f"Task server running at http://{host}:{port}")
    print(f"Using data file: {data_file}")
    print("Press Ctrl+C to stop.")
    server.serve_forever()
