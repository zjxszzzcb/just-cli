import os
import typer
import shutil
from pathlib import Path
from typing_extensions import Annotated

from just import just_cli, capture_exception, echo


def confirm_action(message: str) -> bool:
    """Prompt user for confirmation"""
    response = input(f"{message} (y/N): ").strip().lower()
    return response in ['y', 'yes']


@just_cli.command(name="cat")
@capture_exception
def cat_file(
    file_paths: Annotated[list[str], typer.Argument(
        help="Files to display",
        show_default=False
    )],
    n: Annotated[bool, typer.Option(
        "--number", "-n",
        help="Number all output lines"
    )] = False
):
    """
    Concatenate and print files.
    """
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i, line in enumerate(lines, 1):
                    if n:
                        echo.echo(f"{i:>6}  {line}", end='')
                    else:
                        echo.echo(line, end='')
        except FileNotFoundError:
            echo.error(f"cat: {file_path}: No such file or directory")
        except Exception as e:
            echo.error(f"cat: {file_path}: {str(e)}")


@just_cli.command(name="ls")
@capture_exception
def list_files(
    path: Annotated[str, typer.Argument(
        help="Directory to list",
        show_default=False
    )] = ".",
    l: Annotated[bool, typer.Option(
        "--long-format", "-l",
        help="Use a long listing format"
    )] = False,
    a: Annotated[bool, typer.Option(
        "--all", "-a",
        help="Do not ignore entries starting with ."
    )] = False
):
    """
    List directory contents.
    """
    try:
        p = Path(path)
        if not p.exists():
            echo.error(f"ls: cannot access '{path}': No such file or directory")
            return

        if not p.is_dir():
            if l:
                stat = p.stat()
                echo.echo(f"-rw-r--r-- 1 user group {stat.st_size:>8} {p.name}")
            else:
                echo.echo(p.name)
            return

        entries = list(p.iterdir())
        if not a:
            entries = [entry for entry in entries if not entry.name.startswith('.')]

        if l:
            for entry in entries:
                stat = entry.stat()
                permissions = "drwxr-xr-x" if entry.is_dir() else "-rw-r--r--"
                size = stat.st_size
                echo.echo(f"{permissions} 1 user group {size:>8} {entry.name}")
        else:
            for entry in entries:
                echo.echo(entry.name)

    except Exception as e:
        echo.error(f"ls: {str(e)}")


@just_cli.command(name="mkdir")
@capture_exception
def make_directory(
    dir_names: Annotated[list[str], typer.Argument(
        help="Directories to create",
        show_default=False
    )],
    p: Annotated[bool, typer.Option(
        "--parents", "-p",
        help="No error if existing, make parent directories as needed"
    )] = False
):
    """
    Create directories.
    """
    for dir_name in dir_names:
        try:
            if p:
                os.makedirs(dir_name, exist_ok=True)
            else:
                os.mkdir(dir_name)
        except Exception as e:
            echo.error(f"mkdir: {dir_name}: {str(e)}")


@just_cli.command(name="rm")
@capture_exception
def remove_files(
    targets: Annotated[list[str], typer.Argument(
        help="Files or directories to remove",
        show_default=False
    )],
    r: Annotated[bool, typer.Option(
        "--recursive", "-r",
        help="Remove directories and their contents recursively"
    )] = False,
    f: Annotated[bool, typer.Option(
        "--force", "-f",
        help="Ignore nonexistent files and arguments, never prompt"
    )] = False
):
    """
    Remove files or directories.
    """
    for target in targets:
        try:
            target_path = Path(target)
            if not target_path.exists():
                if not f:
                    echo.error(f"rm: cannot remove '{target}': No such file or directory")
                continue

            if target_path.is_dir():
                if not r and not f:
                    # Prompt for confirmation when removing directory without -r
                    if not confirm_action(f"rm: descend into directory '{target}'?"):
                        continue
                shutil.rmtree(target_path)
            else:
                os.remove(target_path)
        except Exception as e:
            if not f:
                echo.error(f"rm: {target}: {str(e)}")


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
    r: Annotated[bool, typer.Option(
        "--recursive", "-r",
        help="Copy directories recursively"
    )] = False
):
    """
    Copy files or directories.
    """
    try:
        source_path = Path(source)
        dest_path = Path(destination)

        if not source_path.exists():
            echo.error(f"cp: cannot stat '{source}': No such file or directory")
            return

        if source_path.is_dir():
            if not r:
                # Prompt for confirmation when copying directory without -r
                if not confirm_action(f"cp: -r not specified; omitting directory '{source}'"):
                    return
            if dest_path.exists() and dest_path.is_dir():
                # Copy directory into existing directory
                shutil.copytree(source_path, dest_path / source_path.name)
            else:
                shutil.copytree(source_path, dest_path)
        else:
            shutil.copy2(source_path, dest_path)
    except Exception as e:
        echo.error(f"cp: {str(e)}")


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
    )]
):
    """
    Move or rename files or directories.
    """
    try:
        source_path = Path(source)
        dest_path = Path(destination)

        if not source_path.exists():
            echo.error(f"mv: cannot stat '{source}': No such file or directory")
            return

        shutil.move(str(source_path), str(dest_path))
    except Exception as e:
        echo.error(f"mv: {str(e)}")