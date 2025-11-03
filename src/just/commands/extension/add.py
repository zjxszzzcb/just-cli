import shlex
import typer

from typing import List, Optional


from just import echo
from just.core.extension.generator import generate_extension_script
from just.core.extension.utils import split_command_line
from just.tui.extension import ExtensionTUI
from . import ext_cli


@ext_cli.command(name="add", context_settings={"ignore_unknown_options": True})
def add_extension(
    commands: Optional[List[str]] = typer.Argument(
        None,
        help="The command to register as a just extension"
    ),
    tui: bool = typer.Option(
        False,
        "--tui",
        help="Launch TUI to configure the command"
    )
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
    # Split the command line to handle annotations with spaces properly
    just_extension_commands = split_command_line(just_extension_commands)
    echo.echo(str(just_extension_commands))

    # Generate the extension script
    generate_extension_script(
        shlex.join(commands),
        just_extension_commands,
    )


def launch_tui():
    """Launch TUI for configuring extension commands"""

    # Launch the TUI app
    app = ExtensionTUI()
    app.run()
