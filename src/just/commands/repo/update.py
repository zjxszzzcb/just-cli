from typing import List, Optional
from typing_extensions import Annotated

import typer

from just import echo
from just.core.repo import update_repo


def update_repo_cmd(
    args: Annotated[Optional[List[str]], typer.Argument(
        help="Repo name to update. Updates all if omitted."
    )] = None,
) -> None:
    """Update plugin repositories (git pull)."""
    name = args[0] if args else None
    try:
        update_repo(name)
    except ValueError as e:
        echo.error(str(e))
        raise typer.Exit(1)
