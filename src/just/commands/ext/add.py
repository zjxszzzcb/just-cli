import shlex
import typer

from inspect import cleandoc
from typing import List, Optional


from just import echo
from just.core.extension.generator import generate_extension_script
from just.core.extension.utils import split_command_line
from just.tui.extension import ExtensionTUI
from just.utils.user_interaction import get_input


def add_extension(
    ctx: typer.Context,
    tui: bool = typer.Option(
        False,
        "--tui",
        help="Launch TUI to configure the command"
    )
):
    """
    Parse and register a command as a just extension.

    Args:
        ctx: Typer context to capture remaining arguments
        tui: Whether to launch TUI mode
    """
    # Get all arguments after 'just ext add'
    commands = ctx.args
    
    # If no command provided or TUI mode requested, launch TUI
    if not commands or tui:
        launch_tui()
        return

    # Print parsed command for debugging
    echo.echo(str(commands))

    # Show syntax hints
    echo.echo(cleandoc("""
    ============================================================
    Extension Command Syntax:
      Format: just <commands> <placeholder>[var_name:type=default#help]
    
      Syntax breakdown:
        - commands: sub commands list
        - placeholder: The value to replace
        - var_name: Variable name for the parameter
        - type: str|int|float|bool (default: str)
        - default: Optional default value
        - help: Help message for the parameter
    ============================================================
    """))

    just_extension_commands = get_input("Enter extension commands: ")
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