import click
import time

try:
    from tasklist.client.server_client import (
        TaskServerError,
        add_task,
        complete_task,
        delete_task,
        list_completed_tasks,
        list_tasks,
        move_completed_tasks,
    )
    from tasklist.server.app import run_server
except ModuleNotFoundError:
    from client.server_client import (
        TaskServerError,
        add_task,
        complete_task,
        delete_task,
        list_completed_tasks,
        list_tasks,
        move_completed_tasks,
    )
    from server.app import run_server


@click.group()
@click.option(
    "--server-url",
    envvar="TASKLIST_SERVER_URL",
    default="http://127.0.0.1:8000",
    show_default=True,
    help="Base URL for the task server.",
)
@click.pass_context
def cli(ctx, server_url):
    """Task CLI client for a shared task server."""
    ctx.ensure_object(dict)
    ctx.obj["server_url"] = server_url


def _parse_dd_hh_mm_ss(duration_text):
    parts = duration_text.split(":")
    if len(parts) != 4:
        raise click.BadParameter("Duration must be in dd:hh:mm:ss format.")

    try:
        days, hours, minutes, seconds = (int(part) for part in parts)
    except ValueError as exc:
        raise click.BadParameter("Duration must contain only numbers.") from exc

    if days < 0 or hours < 0 or minutes < 0 or seconds < 0:
        raise click.BadParameter("Duration values cannot be negative.")
    if hours > 23:
        raise click.BadParameter("Hours must be between 0 and 23.")
    if minutes > 59:
        raise click.BadParameter("Minutes must be between 0 and 59.")
    if seconds > 59:
        raise click.BadParameter("Seconds must be between 0 and 59.")

    return (days * 86400) + (hours * 3600) + (minutes * 60) + seconds


def _format_dd_hh_mm_ss(total_seconds):
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{days:02d}:{hours:02d}:{minutes:02d}:{seconds:02d}"


def _format_hh_mm_ss(total_seconds):
    total_hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{total_hours:02d}:{minutes:02d}:{seconds:02d}"


def _build_seconds_from_components(days, hours, minutes, seconds):
    if days < 0 or hours < 0 or minutes < 0 or seconds < 0:
        raise click.BadParameter("Timer values cannot be negative.")
    if hours > 23:
        raise click.BadParameter("Hours must be between 0 and 23.")
    if minutes > 59:
        raise click.BadParameter("Minutes must be between 0 and 59.")
    if seconds > 59:
        raise click.BadParameter("Seconds must be between 0 and 59.")

    return (days * 86400) + (hours * 3600) + (minutes * 60) + seconds


@cli.command()
@click.argument("title")
@click.pass_context
def add(ctx, title):
    server_url = ctx.obj["server_url"]
    try:
        task_id = add_task(server_url, title)
    except TaskServerError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Added task #{task_id}: {title}")


@cli.command(name="list")
@click.pass_context
def list_cmd(ctx):
    server_url = ctx.obj["server_url"]
    try:
        tasks = list_tasks(server_url)
    except TaskServerError:
        click.echo("Task server is not running.")
        click.echo("Start it in another terminal with: tasks server")
        click.echo("Or point to a running server: tasks --server-url http://<host>:<port> list")
        return

    if not tasks:
        click.echo("No tasks found.")
        return

    for i, task in enumerate(tasks, start=1):
        status = "✔" if task["completed"] else " "
        created_date = task.get("created_date", "unknown-date")
        click.echo(f"{i}. [{status}] {task['title']} ({created_date})")


@cli.command(name="done-list")
@click.pass_context
def done_list_cmd(ctx):
    server_url = ctx.obj["server_url"]
    try:
        completed_tasks = list_completed_tasks(server_url)
    except TaskServerError as exc:
        raise click.ClickException(str(exc)) from exc

    if not completed_tasks:
        click.echo("No completed tasks found.")
        return

    for i, task in enumerate(completed_tasks, start=1):
        status = "✔" if task.get("completed", False) else " "
        created_date = task.get("created_date", "unknown-date")
        click.echo(f"{i}. [{status}] {task['title']} ({created_date})")


@cli.command(name="move-completed")
@click.pass_context
def move_completed_cmd(ctx):
    server_url = ctx.obj["server_url"]
    try:
        moved_count = move_completed_tasks(server_url)
    except TaskServerError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Moved {moved_count} completed task(s) to completed list.")


@cli.command()
@click.argument("index", type=int)
@click.pass_context
def complete(ctx, index):
    server_url = ctx.obj["server_url"]
    try:
        complete_task(server_url, index)
        click.echo(f"Completed task #{index}")
    except TaskServerError as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command()
@click.argument("index", type=int)
@click.pass_context
def delete(ctx, index):
    server_url = ctx.obj["server_url"]
    try:
        delete_task(server_url, index)
        click.echo(f"Deleted task #{index}")
    except TaskServerError as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command()
@click.argument("duration", required=False)
@click.option("--days", default=0, type=int, show_default=True, help="Days to add.")
@click.option("--hours", default=0, type=int, show_default=True, help="Hours to add (0-23).")
@click.option("--minutes", default=0, type=int, show_default=True, help="Minutes to add (0-59).")
@click.option("--seconds", default=0, type=int, show_default=True, help="Seconds to add (0-59).")
@click.option("--alarm/--no-alarm", default=False, show_default=True, help="Play terminal bell when done.")
def countdown(duration, days, hours, minutes, seconds, alarm):
    """Run a countdown timer in dd:hh:mm:ss format or with component options."""
    total_seconds = 0

    if duration:
        total_seconds += _parse_dd_hh_mm_ss(duration)

    total_seconds += _build_seconds_from_components(days, hours, minutes, seconds)

    if total_seconds == 0:
        click.echo("Countdown is already complete: 00:00:00:00")
        return

    remaining = total_seconds
    while remaining > 0:
        click.echo(f"\rRemaining: {_format_dd_hh_mm_ss(remaining)}", nl=False)
        time.sleep(1)
        remaining -= 1

    click.echo("\rRemaining: 00:00:00:00")
    click.echo("Countdown finished.")
    if alarm:
        click.echo("\a\a\a", nl=False)
        click.echo("Alarm")


@cli.command()
@click.option("--days", default=0, type=int, show_default=True, help="Days to add to elapsed time.")
@click.option("--hours", default=0, type=int, show_default=True, help="Hours to add (0-23).")
@click.option("--minutes", default=0, type=int, show_default=True, help="Minutes to add (0-59).")
@click.option("--seconds", default=0, type=int, show_default=True, help="Seconds to add (0-59).")
def elapsed(days, hours, minutes, seconds):
    """Run an elapsed timer and display hh:mm:ss until stopped."""
    offset_seconds = _build_seconds_from_components(days, hours, minutes, seconds)
    start = time.time()

    try:
        while True:
            elapsed_seconds = int(time.time() - start) + offset_seconds
            click.echo(f"\rElapsed: {_format_hh_mm_ss(elapsed_seconds)}", nl=False)
            time.sleep(1)
    except (KeyboardInterrupt, click.Abort):
        pass

    final_elapsed = int(time.time() - start) + offset_seconds
    click.echo("")
    click.echo(f"Final elapsed: {_format_hh_mm_ss(final_elapsed)}")


@cli.command()
@click.option("--host", default="127.0.0.1", show_default=True, help="Host to bind the server to.")
@click.option("--port", default=8000, show_default=True, type=int, help="Port for the server.")
@click.option(
    "--data-file",
    default="tasks.json",
    show_default=True,
    help="Path to server task data file.",
)
def server(host, port, data_file):
    """Run the shared task server."""
    run_server(host=host, port=port, data_file=data_file)