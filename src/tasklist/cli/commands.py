import click

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


@cli.command(name="completed-list")
@click.pass_context
def completed_list_cmd(ctx):
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