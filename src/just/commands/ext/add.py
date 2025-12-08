import shlex
import typer

from typing import List, Optional


from just import echo
from just.core.extension.generator import generate_extension_script
from just.core.extension.utils import split_command_line
from just.tui.extension import ExtensionTUI


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

    # Show syntax hints
    echo.echo("\n" + "="*60)
    echo.echo("Command Declaration Syntax Hints:")
    echo.echo("  Format: just <command> [ARGUMENT:type=default#help] [--option VALUE:type#help]")
    echo.echo("")
    echo.echo("  Examples:")
    echo.echo("    just docker inspect-container CONTAINER_ID:str#container identifier")
    echo.echo("    just api-call endpoint:str=https://api.example.com --method GET:type=str")
    echo.echo("")
    echo.echo("  ✓ Valid: letters, numbers, underscores (e.g., inspect_container)")
    echo.echo("  ✗ Special chars: -, /, . will be auto-replaced with _")
    echo.echo("  ✓ Numeric: commands like '123' become 'num_123'")
    echo.echo("="*60 + "\n")

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
