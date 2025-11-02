import os
from inspect import cleandoc
from pathlib import Path
from typing import List, Tuple

from just.core.extension.parser import parse_command_structure, Argument
from just.core.extension.utils import search_existing_script


def validate_command_input(just_commands: List[str]) -> None:
    """
    Validate the command input structure.

    Args:
        just_commands: List of command parts to validate

    Raises:
        ValueError: If command structure is invalid
    """
    if not just_commands:
        raise ValueError("Command list cannot be empty")


def get_command_paths(just_commands: List[str]) -> Tuple[Path, Path]:
    """
    Get the paths for command script and directory.

    Args:
        just_commands: List of command parts

    Returns:
        Tuple of (script_path, directory_path)
    """
    # Remove 'just' if it's the first command
    commands = just_commands.copy()
    if commands and commands[0] == 'just':
        commands.pop(0)

    if not commands:
        raise ValueError("No command specified")

    # Calculate paths - extensions for extension commands
    extensions_dir = Path(__file__).parent.parent.parent / 'extensions'

    script_path = Path(os.path.join(extensions_dir, *commands) + '.py')
    directory_path = script_path.parent

    return script_path, directory_path


def ensure_command_directories_exist(just_commands: List[str]) -> None:
    """
    Ensure all necessary command directories exist.

    Args:
        just_commands: List of command parts
    """
    # Remove 'just' if it's the first command
    commands = just_commands.copy()
    if commands and commands[0] == 'just':
        commands.pop(0)

    if not commands:
        return

    extensions_dir = Path(__file__).parent.parent.parent / 'extensions'

    # Create intermediate directories
    for i in range(len(commands) - 1):
        dir_path = Path(os.path.join(extensions_dir, *commands[:i+1]))
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)


def generate_package_init_files(just_commands: List[str]) -> None:
    """
    Generate __init__.py files for command packages.

    Args:
        just_commands: List of command parts
    """
    # Remove 'just' if it's the first command
    commands = just_commands.copy()
    if commands and commands[0] == 'just':
        commands.pop(0)

    if not commands:
        return

    extensions_dir = Path(__file__).parent.parent.parent / 'extensions'
    commands_dir = Path(__file__).parent.parent.parent / 'commands'

    # Create __init__.py files for intermediate packages
    for i in range(len(commands) - 1):
        package_dir = Path(os.path.join(extensions_dir, *commands[:i+1]))
        init_file = package_dir / '__init__.py'

        if not init_file.exists():
            if i == 0:
                # Check if the parent command already exists in commands directory
                parent_init_file = Path(os.path.join(commands_dir, commands[0], '__init__.py'))
                if parent_init_file.exists():
                    # Import from commands directory instead of creating new CLI
                    content = cleandoc(f"""
                    from just.commands.{commands[0]} import {commands[0]}_cli


                    __all__ = ["{commands[0]}_cli"]
                    """)
                else:
                    # Create new CLI as usual
                    content = cleandoc(f"""
                    from just import just_cli, create_typer_app


                    {commands[0]}_cli = create_typer_app(name="{commands[0]}")
                    # Add the CLI to the just CLI
                    just_cli.add_typer({commands[0]}_cli)

                    __all__ = ["{commands[0]}_cli"]
                    """)
            else:
                content = cleandoc(f"""
                from just import create_typer_app

                from .. import {commands[i-1]}_cli


                {commands[i]}_cli = create_typer_app(name="{commands[i]}")
                # Add the CLI to the parent CLI
                {commands[i-1]}_cli.add_typer({commands[i]}_cli)

                __all__ = ["{commands[i]}_cli"]
                """)

            with open(init_file, 'w', encoding='utf-8') as f:
                f.write(content)


def generate_function_signature(arguments: List[Argument], options: dict) -> str:
    """
    Generate the function signature for the Typer command.

    Args:
        arguments: List of command arguments
        options: Dictionary of command options

    Returns:
        Formatted function signature string
    """
    all_params = []

    # Track variable names to avoid duplicates
    used_names = set()

    # Add arguments
    for arg in arguments:
        # Ensure unique variable names
        var_name = arg.name
        counter = 1
        while var_name in used_names:
            var_name = f"{arg.name}_{counter}"
            counter += 1
        used_names.add(var_name)

        default_assignment = ""
        if arg.default_value is not None:
            # Handle string default values properly
            if isinstance(arg.default_value, str):
                default_assignment = f" = '{arg.default_value}'"
            else:
                default_assignment = f" = {arg.default_value}"
        all_params.append(
            f"    {var_name}: Annotated[{arg.type.__name__}, typer.Argument(\n"
            f"        help={repr(arg.help)},\n"
            f"        show_default=False\n"
            f"    )]{default_assignment}"
        )

    # Add options processing
    for flag, opt in options.items():
        # Ensure unique variable names
        var_name = opt.name
        counter = 1
        while var_name in used_names:
            var_name = f"{opt.name}_{counter}"
            counter += 1
        used_names.add(var_name)

        default_assignment = ""
        if opt.default_value is not None:
            # Handle string default values properly
            if isinstance(opt.default_value, str):
                default_assignment = f" = '{opt.default_value}'"
            else:
                default_assignment = f" = {opt.default_value}"
        # Determine if it's a boolean flag option
        elif opt.type.__name__ == 'bool':
            # Boolean flag without explicit default - treat as False default
            default_assignment = " = False"

        all_params.append(
            f"    {var_name}: Annotated[{opt.type.__name__}, typer.Option(\n"
            f"        {repr(f'--{flag}')},\n"
            f"        help={repr(opt.help)},\n"
            f"        show_default=False\n"
            f"    )]{default_assignment}"
        )

    # Join all parameters with commas
    if not all_params:
        return '\n'

    formatted_params = []
    for i, param in enumerate(all_params):
        if i < len(all_params) - 1:
            formatted_params.append(param + ",\n")
        else:
            formatted_params.append(param + "\n")

    return ''.join(formatted_params) + '\n'


def generate_command_replacements(arguments: List[Argument], options: dict) -> str:
    """
    Generate the command replacement logic.

    Args:
        arguments: List of command arguments
        options: Dictionary of command options

    Returns:
        Formatted command replacement string
    """
    # Create mapping of original names to new names
    name_mapping = {}

    # Map arguments
    arg_counter = 1
    for arg in arguments:
        var_name = arg.name
        while var_name in name_mapping.values():
            var_name = f"{arg.name}_{arg_counter}"
            arg_counter += 1
        name_mapping[arg.name] = var_name

    # Map options
    opt_counter = 1
    for flag, opt in options.items():
        var_name = opt.name
        while var_name in name_mapping.values():
            var_name = f"{opt.name}_{opt_counter}"
            opt_counter += 1
        name_mapping[opt.name] = var_name

    # Generate replacements for arguments
    command_replacements = []
    for arg in arguments:
        var_name = name_mapping[arg.name]
        command_replacements.append(
            f"    command = command.replace({repr(arg.repl_identifier)}, str({var_name}))"
        )

    # Generate replacements for options
    for flag, opt in options.items():
        var_name = name_mapping[opt.name]
        # For boolean flags, only add the flag if True
        if opt.type.__name__ == 'bool':
            command_replacements.append(
                f"    if {var_name}:"
            )
            # For boolean flags, we typically just want to include the flag itself, not its value
            command_replacements.append(
                f"        command = command.replace({repr(opt.repl_identifier)}, '{opt.repl_identifier}')"
            )
        else:
            command_replacements.append(
                f"    command = command.replace({repr(opt.repl_identifier)}, str({var_name}))"
            )

    if command_replacements:
        command_replacements[0] = command_replacements[0].lstrip()
        return '\n'.join(command_replacements)

    return ""


def assemble_typer_script_content(
    custom_command: str,
    parent_cmd: str,
    sub_cmd: str,
    signature: str,
    replacements: str
) -> str:
    """
    Assemble the complete Typer script content.

    Args:
        custom_command: The original command template
        parent_cmd: Parent command name
        sub_cmd: Sub command name
        signature: Function signature
        replacements: Command replacement logic

    Returns:
        Complete script content
    """
    template = '''import shlex
import subprocess
import typer

from typing_extensions import Annotated

from just import create_typer_app
from . import {parent_cmd}_cli


{sub_cmd}_cli = create_typer_app()
# Add the CLI to the parent CLI
{parent_cmd}_cli.add_typer({sub_cmd}_cli)


@{sub_cmd}_cli.command(name="{sub_cmd}")
def main(
{signature}
):
    command = r"""
    {custom_command}
    """.strip()
    {replacements}
    subprocess.run(shlex.split(command))
'''

    return template.format(
        custom_command=custom_command,
        parent_cmd=parent_cmd,
        sub_cmd=sub_cmd,
        signature=signature.rstrip('\n'),
        replacements=replacements
    )


def generate_extension_script(custom_command: str, just_commands: List[str]) -> None:
    """
    Generate a complete extension script.

    Args:
        custom_command: The original command template
        just_commands: List of command parts

    Raises:
        FileExistsError: If the script already exists
        ValueError: If command structure is invalid
    """
    # Validate input
    validate_command_input(just_commands)

    # Parse command structure
    parsed_commands, arguments, options = parse_command_structure(just_commands)

    # Check if script already exists
    exist, final_expect_script_path = search_existing_script(parsed_commands)
    if exist:
        raise FileExistsError(f"{final_expect_script_path} already exists")

    # Remove 'just' if it's the first command
    commands = parsed_commands.copy()
    if commands and commands[0] == 'just':
        commands.pop(0)

    if not commands:
        raise ValueError("No command specified")

    # Ensure directories exist
    ensure_command_directories_exist(parsed_commands)

    # Generate package init files
    generate_package_init_files(parsed_commands)

    # Determine command hierarchy
    just_parent_command = f"{commands[-2]}" if len(commands) > 1 else "just"
    just_sub_command = commands[-1]

    # Generate function signature
    signature = generate_function_signature(arguments, options)

    # Generate command replacements
    replacements = generate_command_replacements(arguments, options)

    # Assemble final content
    content = assemble_typer_script_content(
        custom_command,
        just_parent_command,
        just_sub_command,
        signature,
        replacements
    )

    # Write the script file
    script_path = Path(final_expect_script_path)
    script_path.parent.mkdir(parents=True, exist_ok=True)

    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(content)