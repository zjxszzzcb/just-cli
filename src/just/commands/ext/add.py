import subprocess
import typer
from typing import List

from just import echo
from just.core.extension.generator import generate_extension_script
from just.core.extension.utils import split_command_line
from just.tui.extension import ExtensionTUI
from just.utils.user_interaction import get_input, confirm_action


def show_success(script_path, commands):
    """Show success message and run -h to display help."""
    echo.green(f"\n✅ Extension created successfully!")
    echo.cyan(f"   File: {script_path}")
    echo.echo("")

    # Run -h to show help
    echo.echo("Help for the new extension:")
    echo.echo("-" * 40)
    cmd_str = ' '.join(['just'] + commands + ['-h'])
    subprocess.run(cmd_str, shell=True)


def add_extension(
    ctx: typer.Context,
    yes: bool = typer.Option(
        False,
        "--yes", "-y",
        help="Auto-confirm overwrite if extension exists"
    ),
    tui: bool = typer.Option(
        False,
        "--tui",
        help="Launch TUI to configure the command"
    ),
    command: List[str] = typer.Option(
        None,
        "--command", "-c",
        help="Shell command to register. May be repeated for sequential "
             "commands (run in order, stop on first failure). "
             "Mutually exclusive with positional command args."
    )
):
    """
    Register a command as a just extension.

    \b
    USAGE:
        just ext add <command> [args...]
        just ext add -c "<command>" [-c "<command>" ...]
        Enter: just <name> <syntax...>

    \b
    SYNTAX (3 patterns):

    \b
    1. ARGUMENT (replace placeholder):
       PLACEHOLDER[var:type=default#help]
       → command.replace(PLACEHOLDER, var)

    \b
    2. OPTION (replace placeholder):
       --flag PLACEHOLDER[var:type]
       → command.replace(PLACEHOLDER, var)

    \b
    3. OPTION ALIAS (append to command):
       -s/--source[target:type]
       → User runs --target, appends --source to command
    """
    # Get all arguments after 'just ext add' (positional command tokens)
    positional_commands = ctx.args

    # -c/--command and positional args are mutually exclusive
    if command and positional_commands:
        echo.red("Error: -c/--command cannot be combined with positional command args.")
        raise typer.Exit(code=1)

    # If no command provided either way, or TUI mode requested, launch TUI
    if not command and (not positional_commands or tui):
        launch_tui()
        return

    # Normalize into a list of command strings.
    # Positional tokens form a single command (joined as-is, no escaping);
    # each -c is one complete command string as the user typed it.
    if command:
        commands = command
    else:
        commands = [' '.join(positional_commands)]

    # Prompt for extension syntax
    just_extension_commands = get_input("Enter extension commands: ")
    # Split the command line to handle annotations with spaces properly
    just_extension_commands = split_command_line(just_extension_commands)

    # Generate the extension script, with overwrite confirmation if exists
    try:
        script_path, ext_commands = generate_extension_script(
            commands,
            just_extension_commands,
        )
        show_success(script_path, ext_commands)
    except FileExistsError as e:
        echo.yellow(f"Warning: {e}")
        if yes or confirm_action("Do you want to overwrite the existing extension?"):
            script_path, ext_commands = generate_extension_script(
                commands,
                just_extension_commands,
                overwrite=True
            )
            show_success(script_path, ext_commands)
        else:
            echo.echo("Cancelled.")
            raise typer.Exit(code=0)


def launch_tui():
    """Launch TUI for configuring extension commands"""

    # Launch the TUI app
    app = ExtensionTUI()
    app.run()