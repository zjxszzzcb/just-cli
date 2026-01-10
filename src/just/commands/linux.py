import os
import typer
import shutil
from pathlib import Path
from typing_extensions import Annotated

from just import just_cli, capture_exception, echo
from just.utils.file_utils import read_file_text
from just.utils import confirm_action


@just_cli.command(name="cat")
@capture_exception
def cat_file(
    file_paths: Annotated[list[str], typer.Argument(
        help="Files to display",
        show_default=False
    )],
    with_line_numbers: Annotated[bool, typer.Option(
        "--number", "-n",
        help="Number all output lines"
    )] = False
):
    """
    Concatenate and print files.
    """
    for file_path in file_paths:
        if os.path.isdir(file_path):
            echo.red(f"cat: {file_path} is a directory")
            exit(1)
        try:
            echo.echo(read_file_text(file_path, with_line_numbers=with_line_numbers))
        except FileNotFoundError:
            echo.red(f"cat: The file {file_path} does not exist")
            exit(1)


@just_cli.command(name="ls")
@capture_exception
def list_files(
    path: Annotated[str, typer.Argument(
        help="Directory to list",
        show_default=False
    )] = ".",
    long_format: Annotated[bool, typer.Option(
        "-l",
        help="Use a long listing format"
    )] = False,
    all_format: Annotated[bool, typer.Option(
        "--all", "-a",
        help="Do not ignore entries starting with ."
    )] = False
):
    """
    List directory contents.
    """
    p = Path(path)
    if not p.exists():
        echo.red(f"ls: cannot access '{path}': No such file or directory")
        exit(1)

    if not p.is_dir():
        if long_format:
            stat = p.stat()
            echo.echo(f"-rw-r--r-- 1 user group {stat.st_size:>8} {p.name}")
        else:
            echo.echo(p.name)
        return

    entries = list(p.iterdir())
    if not all_format:
        entries = [entry for entry in entries if not entry.name.startswith('.')]

    if long_format:
        for entry in entries:
            stat = entry.stat()
            permissions = "drwxr-xr-x" if entry.is_dir() else "-rw-r--r--"
            size = stat.st_size
            echo.echo(f"{permissions} 1 user group {size:>8} {entry.name}")
    else:
        for entry in entries:
            echo.echo(entry.name)


@just_cli.command(name="mkdir")
@capture_exception
def make_directory(
    dir_names: Annotated[list[str], typer.Argument(
        help="Directories to create",
        show_default=False
    )],
    make_parents: Annotated[bool, typer.Option(
        "--parents", "-p",
        help="No error if existing, make parent directories as needed"
    )] = False
):
    """
    Create directories.
    """
    for dir_name in dir_names:
        if make_parents:
            os.makedirs(dir_name, exist_ok=True)
        else:
            os.mkdir(dir_name)


@just_cli.command(name="rm")
@capture_exception
def remove_files(
    targets: Annotated[list[str], typer.Argument(
        help="Files or directories to remove",
        show_default=False
    )],
    recursive: Annotated[bool, typer.Option(
        "--recursive", "-r",
        help="Remove directories and their contents recursively"
    )] = False,
    yes: Annotated[bool, typer.Option(
        "--yes", "-y",
        help="Skip confirmation prompts"
    )] = False
):
    """
    Remove files or directories.
    """
    for target in targets:
        target_path = Path(target)
        if not target_path.exists():
            echo.red(f"rm: cannot remove '{target}': No such file or directory")
            exit(1)
        if target_path.is_dir():
            # Prompt for confirmation when removing directory without -r
            if not recursive and not yes and not confirm_action(f"rm: descend into directory '{target}'?"):
                continue
            shutil.rmtree(target_path)
        else:
            os.remove(target_path)


@just_cli.command(name="cp")
@capture_exception
def copy_files(
    source: Annotated[str, typer.Argument(
        help="Source file or directory",
        show_default=False
    )],
    destination: Annotated[str, typer.Argument(
        help="Destination file or directory",
        show_default=False
    )],
    recursive: Annotated[bool, typer.Option(
        "--recursive", "-r",
        help="Copy directories recursively"
    )] = False,
    yes: Annotated[bool, typer.Option(
        "--yes", "-y",
        help="Skip confirmation prompts"
    )] = False
):
    """
    Copy files or directories.
    """
    source_path = Path(source)
    dest_path = Path(destination)

    if not source_path.exists():
        echo.red(f"cp: cannot stat '{source}': No such file or directory")
        exit(1)


    if source_path.is_dir():
        if not recursive:
            # Prompt for confirmation when copying directory without -r
            if not yes and not confirm_action(f"cp: -r not specified; omitting directory '{source}'"):
                exit(1)
        if dest_path.exists() and dest_path.is_dir():
            # Copy directory into existing directory
            shutil.copytree(source_path, dest_path / source_path.name)
        else:
            shutil.copytree(source_path, dest_path)
    else:
        shutil.copy2(source_path, dest_path)


@just_cli.command(name="mv")
@capture_exception
def move_files(
    source: Annotated[str, typer.Argument(
        help="Source file or directory",
        show_default=False
    )],
    destination: Annotated[str, typer.Argument(
        help="Destination file or directory",
        show_default=False
    )],
    yes: Annotated[bool, typer.Option(
        "--yes", "-y",
        help="Skip confirmation prompts"
    )] = False
):
    """
    Move or rename files or directories.
    """
    source_path = Path(source)
    dest_path = Path(destination)

    if not source_path.exists():
        echo.red(f"mv: cannot stat '{source}': No such file or directory")
        exit(1)
    if dest_path.exists() and not yes and not confirm_action(f"mv: overwrite '{destination}'?"):
        exit(1)

    shutil.move(str(source_path), str(dest_path))
