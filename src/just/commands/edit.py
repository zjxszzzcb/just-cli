import os
import typer

from pathlib import Path
from typing_extensions import Annotated

from just import just_cli, config, echo, capture_exception, update_env_config
from just.tui import FileEditor
from just.utils import execute_command


__package_dir__ = os.path.dirname(os.path.dirname(__file__))

INTERNAL_FILES = {
    "config": str(Path(__file__).parent.parent / ".env")
}


def edit_file_by_textual(file_path):
    """Launch the TUI file editor for the specified file"""
    editor = FileEditor(file_path)
    editor.run()


@just_cli.command(name="edit")
@capture_exception
def edit_file(
    file_path: Annotated[str, typer.Argument(
        help="The file to edit",
        show_default=False
    )]
):
    """
    Edit file.
    """
    if file_path.lower() in INTERNAL_FILES:
        file_path = INTERNAL_FILES[file_path.lower()]

    if config.JUST_EDIT_USE_TOOL == 'unk':
        option = input("Which editor would you like to use? [e]dit or [t]extual: ")
        if option.lower() == 't':
            echo.info(f'Set JUST_EDIT_USE_TOOL="textual"')
            update_env_config("JUST_EDIT_USE_TOOL", "textual")
            os.environ["JUST_EDIT_USE_TOOL"] = "textual"
        else:
            echo.info(f'Set JUST_EDIT_USE_TOOL="edit"')
            update_env_config("JUST_EDIT_USE_TOOL", "edit")
            os.environ["JUST_EDIT_USE_TOOL"] = "edit"

    if config.JUST_EDIT_USE_TOOL == 'edit':
        execute_command(f"edit {file_path}")
    elif os.path.getsize(file_path) > 4096 * 1024:
        echo.warning("File is too large for textual editor. Try to use microsoft edit instead.")
        execute_command(f"edit {file_path}")
    else:
        edit_file_by_textual(file_path)
