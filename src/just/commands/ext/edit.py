import os
import typer
from pathlib import Path
from typing import List, Optional

from just.utils.echo_utils import echo, red, green, yellow, cyan
from just.core.config import get_extension_dir
from just.tui.editor import FileEditor


def edit_extension(
    commands: List[str] = typer.Argument(
        ...,
        help="The extension command to edit (e.g., docker ip)"
    )
):
    """
    Edit an existing just extension using the built-in editor.

    Args:
        commands: List of command parts (e.g., ['docker', 'ip'])
    """
    if not commands:
        red("Error: No command specified")
        raise typer.Exit(code=1)

    # Get the extension directory
    extensions_dir = get_extension_dir()

    # Sanitize command names (same as in add.py)
    from just.core.extension.validator import sanitize_command_path
    sanitized_commands, transformation_notes = sanitize_command_path(commands)

    # Show transformation notes if any
    if transformation_notes:
        echo()
        cyan("Note: Command name sanitization applied:")
        for note in transformation_notes:
            echo(f"  - {note}")
        echo()

    # Construct the file path
    script_path = Path(extensions_dir, *sanitized_commands).with_suffix('.py')

    # Check if the file exists
    if not script_path.exists():
        red(f"Error: Extension command '{' '.join(commands)}' not found")
        yellow(f"Expected location: {script_path}")
        echo()
        cyan("Tip: Use 'just ext list' to see all available extensions")
        raise typer.Exit(code=1)

    # Launch the editor
    cyan(f"Opening extension: {' '.join(sanitized_commands)}")
    cyan(f"File: {script_path}")
    echo()
    echo("Editor Controls:")
    echo("  Ctrl+S - Save")
    echo("  Ctrl+Q or Escape - Quit")
    echo()

    try:
        app = FileEditor(str(script_path))
        app.run()
        echo()
        green("Editor closed.")
    except KeyboardInterrupt:
        echo()
        yellow("Editor cancelled.")
    except Exception as e:
        echo()
        red(f"Error opening editor: {e}")
        raise typer.Exit(code=1)