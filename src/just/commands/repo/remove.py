from typing_extensions import Annotated

import typer

from just import echo, confirm_action
from just.core.repo import remove_repo


def remove_repo_cmd(
    name: Annotated[str, typer.Argument(help="Name of the repo to remove")],
    yes: Annotated[bool, typer.Option("--yes", "-y", help="Skip confirmation")] = False,
) -> None:
    """Remove a plugin repository."""
    if not yes:
        if not confirm_action(f"Remove repo '{name}'?"):
            echo.info("Cancelled.")
            return

    try:
        remove_repo(name)
    except ValueError as e:
        echo.error(str(e))
        raise typer.Exit(1)
