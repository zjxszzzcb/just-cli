import os
import typer

from pathlib import Path
from typing_extensions import Annotated

from just import just_cli, capture_exception
from just.core.config import get_env_config_file
from just.tui import FileEditor


INTERNAL_FILES = {
    "config": str(get_env_config_file())
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

    edit_file_by_textual(file_path)
