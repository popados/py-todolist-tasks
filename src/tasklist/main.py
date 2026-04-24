try:
    from tasklist.cli.commands import cli
except ModuleNotFoundError:
    # Allow running main.py directly from src/tasklist.
    from cli.commands import cli


def main():
    cli()


if __name__ == "__main__":
    main()
