from pathlib import Path

from just import just_cli, capture_exception
from just.tui.workspace import WorkspaceApp


@just_cli.command(name="code")
@capture_exception
def workspace_command(
    path: str = ".",
):
    """
    Open a VSCode-style workspace editor.
    """
    workspace_path = Path(path).resolve()
    if not workspace_path.exists():
        print(f"Error: Path does not exist: {workspace_path}")
        return

    app = WorkspaceApp(str(workspace_path))
    app.run()
