import re
from importlib.metadata import version as get_version
from pathlib import Path

import typer
from typer import Context
from typer.core import TyperGroup

from typing import Optional


class NormalizedGroup(TyperGroup):
    """
    A custom TyperGroup that normalizes command names by replacing
    all special characters with underscores when resolving commands.
    This allows users to type `my-echo` or `my.echo` to invoke `my_echo`.
    """

    def get_command(self, ctx: Context, cmd_name: str):
        # First try the original command name
        cmd = super().get_command(ctx, cmd_name)
        if cmd is not None:
            return cmd

        # If not found, try normalizing (replace all non-alphanumeric chars with underscores)
        normalized_name = re.sub(r'[^a-zA-Z0-9]', '_', cmd_name)
        if normalized_name != cmd_name:
            return super().get_command(ctx, normalized_name)

        return None


def get_just_version() -> str:
    """Get just-cli version from package metadata."""
    try:
        return get_version("just-cli")
    except Exception:
        return "unknown"


def detect_install_method() -> str:
    """
    Detect how just-cli was installed.

    Returns one of: 'uv', 'pip', 'unknown'
    """
    install_path = str(Path(__file__).resolve())

    # uv tool environments live under .local/share/uv/tools/
    if "uv/tools/just-cli" in install_path:
        return "uv"

    # Regular pip/venv environments
    if "site-packages" in install_path:
        return "pip"

    return "unknown"


def create_typer_app(
    name: Optional[str] = None,
    help: Optional[str] = None,
) -> typer.Typer:
    typer_app = typer.Typer(
        name=name,
        help=help,
        add_completion=False,
        cls=NormalizedGroup,  # Use custom group for command resolution
        context_settings={
            "help_option_names": ["-h", "--help"]
        }
    )

    return typer_app


def show_help(app: typer.Typer, command_name: str = ""):
    click_command = typer.main.get_command(app)

    if not command_name:
        # 显示主帮助
        typer.echo(click_command.get_help(click_command.make_context("just", [])))
        return

    # 查找子命令
    if hasattr(click_command, 'commands') and command_name in getattr(click_command, 'commands'):
        sub_command = click_command.commands[command_name]
        typer.echo(sub_command.get_help(sub_command.make_context(command_name, [])))
    else:
        typer.echo(f"Command '{command_name}' not found")