import shutil
import typer
from pathlib import Path
from typing import List

from just.utils.echo_utils import red, green, yellow, cyan, echo
from just.core.config import get_extension_dir
from just.utils.user_interaction import confirm_action


def remove_extension(
    commands: List[str] = typer.Argument(
        ...,
        help="The extension command to remove (e.g., docker ip)"
    ),
    force: bool = typer.Option(
        False,
        "-y",
        help="Confirm to remove the extension"
    )
):
    """
    Remove an existing just extension.

    Args:
        commands: List of command parts (e.g., ['docker', 'ip'])
        force: Skip confirmation prompt
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
        cyan("Note: Command name sanitization applied:")
        for note in transformation_notes:
            echo(f"  - {note}")

    # Construct the file path
    script_path = Path(extensions_dir, *sanitized_commands).with_suffix('.py')

    # Check if the file exists
    if not script_path.exists():
        red(f"Error: Extension command '{' '.join(commands)}' not found")
        yellow(f"Expected location: {script_path}")
        cyan("Tip: Use 'just ext list' to see all available extensions")
        raise typer.Exit(code=1)

    # Confirm deletion
    if not force:
        echo(f"About to remove extension: {' '.join(sanitized_commands)}")
        echo(f"File: {script_path}")
        if not confirm_action("Are you sure you want to delete this extension?"):
            yellow("Cancelled.")
            raise typer.Exit(code=0)

    try:
        # Delete the script file
        script_path.unlink()
        green(f"Removed: {script_path}")

        # Clean up empty parent directories and orphan __init__.py files
        cleanup_count = _cleanup_empty_directories(script_path.parent, extensions_dir)
        if cleanup_count > 0:
            cyan(f"Cleaned up {cleanup_count} empty director{'ies' if cleanup_count > 1 else 'y'}")
        green(f"Extension '{' '.join(sanitized_commands)}' removed successfully!")

    except PermissionError:
        red(f"Error: Permission denied when removing {script_path}")
        raise typer.Exit(code=1)
    except Exception as e:
        red(f"Error removing extension: {e}")
        raise typer.Exit(code=1)


def _cleanup_empty_directories(start_dir: Path, stop_at: Path) -> int:
    """
    Clean up empty directories and orphan __init__.py files.

    Walks up from start_dir to stop_at, removing:
    - Empty directories
    - Directories containing only __init__.py (orphan packages)

    Args:
        start_dir: Directory to start cleaning from
        stop_at: Directory to stop at (exclusive, won't be deleted)

    Returns:
        Number of directories cleaned up
    """
    cleaned = 0
    current = start_dir

    while current != stop_at and current.is_relative_to(stop_at):
        if not current.exists():
            current = current.parent
            continue

        # Get directory contents (excluding __pycache__)
        contents = [
            item for item in current.iterdir()
            if item.name != '__pycache__'
        ]

        # Check if directory is empty or only contains __init__.py
        if len(contents) == 0:
            # Empty directory, remove it
            # Also remove __pycache__ if it exists
            pycache = current / '__pycache__'
            if pycache.exists():
                shutil.rmtree(pycache)
            current.rmdir()
            cleaned += 1
        elif len(contents) == 1 and contents[0].name == '__init__.py':
            # Only contains __init__.py (orphan package), remove both
            contents[0].unlink()
            pycache = current / '__pycache__'
            if pycache.exists():
                shutil.rmtree(pycache)
            current.rmdir()
            cleaned += 1
        else:
            # Directory has other contents, stop cleaning
            break

        current = current.parent

    return cleaned
