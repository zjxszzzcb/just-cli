from pathlib import Path
from typing_extensions import Annotated

import typer

from just import just_cli, capture_exception
from just.tui.workspace import WorkspaceApp


@just_cli.command(name="code")
@capture_exception
def workspace_command(
    workdir: Annotated[str, typer.Argument(help="Working directory")] = ".",
):
    """
    Open a VSCode-style workspace editor.
    """
    workspace_path = Path(workdir).resolve()
    if not workspace_path.exists():
        print(f"Error: Path does not exist: {workspace_path}")
        return

    app = WorkspaceApp(str(workspace_path))
    app.run()
