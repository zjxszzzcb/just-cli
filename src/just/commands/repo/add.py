from typing_extensions import Annotated

import typer

from just import echo
from just.core.repo import add_repo


def add_repo_cmd(
    name: Annotated[str, typer.Argument(help="Local name for the repo")],
    url: Annotated[str, typer.Argument(help="Git remote URL")],
) -> None:
    """Add a plugin repository from a Git URL."""
    try:
        add_repo(name, url)
    except (ValueError, RuntimeError) as e:
        echo.error(str(e))
        raise typer.Exit(1)
