
<!-- markdownlint-disable MD031 -->
<!-- markdownlint-disable MD032 -->
<!-- markdownlint-disable MD033 -->
<!-- markdownlint-disable MD036 -->
<!-- markdownlint-disable MD041 -->
<div id="top-of-doc"></div>

# Readme File | tasklist-py | April/14/2026 |

[Github](https://github.com/popados) | [Jump to End](#end-of-doc)

***

A server-based task manager built with Python and Click.

## Quick Start (Server + Client) | `tasks` command

1. Install the CLI:

```bash
pip install -e .
```

2. Start the shared server (one machine/process):

```bash
tasks server --host 127.0.0.1 --port 8000 --data-file tasks.json
```

3. From this or any other terminal, run client commands against that server:

```bash
tasks --server-url http://127.0.0.1:8000 add "Buy groceries"
tasks --server-url http://127.0.0.1:8000 list
tasks --server-url http://127.0.0.1:8000 complete 1
tasks --server-url http://127.0.0.1:8000 delete 1
```

If you set environment variable `TASKLIST_SERVER_URL`, you can skip `--server-url` on each command.

## Installation Notes

To use the Python 3.14 installation directly:

```bash
C:/Users/popad/AppData/Local/Programs/Python/Python314/python.exe -m pip install -e .
```

If `tasks` is not found, use the full script path:

```bash
C:\Users\popad\AppData\Local\Programs\Python\Python314\Scripts\tasks.exe --help
```

You can also add `C:\Users\popad\AppData\Local\Programs\Python\Python314\Scripts` to your PATH.

## Run Without Installing

From project root:

```bash
python src/tasklist/main.py server --host 127.0.0.1 --port 8000 --data-file tasks.json
python src/tasklist/main.py --server-url http://127.0.0.1:8000 list
```

From `src/tasklist`:

```bash
cd src/tasklist
python main.py --server-url http://127.0.0.1:8000 list
```

***

**Loading .env**

Your CLI already supports this through the env var binding in Click, so once TASKLIST_SERVER_URL is in your shell environment, tasks commands will use it automatically.

- Load from .env in Git Bash (recommended):

```bash
set -a
source .env
set +a
tasks list
tasks add "from env"
```

- One-command temporary value (does not persist):

```bash
TASKLIST_SERVER_URL=http://127.0.0.1:8000 tasks list
```

Verify it is loaded:

```bash
echo "$TASKLIST_SERVER_URL"
```
Make it automatic each session (optional):
- Add this line to your shell profile (for example ~/.bashrc), then restart terminal:

```bash
set -a
source /c/Users/popad/OneDrive/Desktop/2025-git-clones/tasklist-py/.env
set +a
```
- Why set -a is used:
  - It auto-exports variables loaded by source, so TASKLIST_SERVER_URL becomes visible to child processes like tasks.

## Data File Behavior

Tasks are saved on the server machine in the file passed to `tasks server --data-file`.

- All clients see the same list when they use the same server URL.
- Client working directory no longer controls where tasks are stored.

### File Responsibilities

- `src/tasklist/main.py`
  - Entry point for the app.
  - Loads the CLI group and starts command handling.

- `src/tasklist/cli/commands.py`
  - Defines CLI commands: `server`, `add`, `list`, `complete`, and `delete`.
  - `server` starts the shared HTTP task server.
  - Client commands call the server using `--server-url`.

- `src/tasklist/client/server_client.py`
  - HTTP client used by CLI commands.
  - Sends requests to the server and returns parsed task data.

- `src/tasklist/server/app.py`
  - HTTP server implementation for shared tasks.
  - Exposes `/tasks` endpoints and persists data via service/storage layers.

- `src/tasklist/services/task_service.py`
  - Contains task business logic.
  - Validates task indexes for `complete` and `delete`.
  - Calls storage functions to read/write tasks.

- `src/tasklist/db/storage.py`
  - Handles persistence using JSON.
  - Reads tasks from `tasks.json` and writes updates back to disk.

- `src/tasklist/__init__.py`, `src/tasklist/cli/__init__.py`, `src/tasklist/client/__init__.py`, `src/tasklist/server/__init__.py`, `src/tasklist/services/__init__.py`, `src/tasklist/db/__init__.py`
  - Mark directories as Python packages.

***

## Project Structure

```bash
 tasklist-py/
 ├── pyproject.toml
 ├── README.md
 └── src/
     └── tasklist/
         ├── __init__.py
         ├── main.py
         ├── cli/
         │   ├── __init__.py
         │   └── commands.py
         ├── client/
         │   ├── __init__.py
         │   └── server_client.py
         ├── server/
         │   ├── __init__.py
         │   └── app.py
         ├── services/
         │   ├── __init__.py
         │   └── task_service.py
         └── db/
             ├── __init__.py
             └── storage.py
```

***

## Commands

***

### Day 01 | 4/14/2026 - Tuesday

Learning how cli applications are put together with python. Learning how imports and structure helps when creating a tool. Using click for options and stuff for the tool. 

TODO:
- Add colors + tables (using Rich)
- Turn it into a global command (tasker instead of python tasker.py)
- Add features like due dates, priorities, or tags
- Persist data in SQLite instead of JSON

***

### Day 02 | 4/15/2026 - Wednesday

Changed to a server_client build so I can check tasks when the server is loaded.

***

## End of Document

***

[Jump to Top](#top-of-doc)

<div id="end-of-doc"></div>

<details>
<summary>
Notes :
</summary>
</details>
