import re
import typer

from typing import List, Optional


from just import echo
from just.utils.ext_utils import create_typer_script
from just.tui.extension import ExtensionTUI
from . import ext_cli


@ext_cli.command(name="add", context_settings={"ignore_unknown_options": True})
def add_extension(
    commands: Optional[List[str]] = typer.Argument(None, help="The command to register as a just extension"),
    tui: bool = typer.Option(False, "--tui", help="Launch TUI to configure the command")
):
    """
    Parse and register a command as a just extension.

    Args:
        commands: The commands to register, e.g., "docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' f523e75ca4ef"
        tui: Whether to launch TUI mode
    """
    # If no command provided or TUI mode requested, launch TUI
    if not commands or tui:
        launch_tui()
        return

    # Print parsed command for debugging
    echo.echo(str(commands))

    just_extension_commands = input("Enter extension commands: ")
    just_extension_commands = re.split(r'\s+', just_extension_commands.strip())
    echo.echo(str(just_extension_commands))
    print(create_typer_script(
        " ".join(commands),
        just_extension_commands,
    ))


def launch_tui():
    """Launch TUI for configuring extension commands"""

    # Launch the TUI app
    app = ExtensionTUI()
    app.run()
