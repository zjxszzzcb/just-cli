import re
import typer

from typing import List, Optional


from just import echo
from just.utils.ext_utils import create_typer_script
from just.tui.extension import ExtensionTUI
from . import ext_cli


def parse_just_commands(command_line: str) -> List[str]:
    """
    Parse JUST CLI command line while preserving annotations with spaces.

    This function handles command lines like:
    "just docker ipv4 --container f523e75ca4ef[container_id:str#docker container id or name]"

    Where the annotation contains spaces that shouldn't be split into separate arguments.

    Args:
        command_line: The command line string to parse

    Returns:
        List of parsed command parts
    """
    # This regex matches annotated parameters as single units, handling nested brackets in help text
    # Pattern: \S*\[.*?\] - non-greedy match for everything in brackets
    # Or: \S+ - regular non-whitespace sequences
    return re.findall(r'\S*\[.*?\]|\S+', command_line.strip())


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
    # Parse the command line to handle annotations with spaces properly
    just_extension_commands = parse_just_commands(just_extension_commands)
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
