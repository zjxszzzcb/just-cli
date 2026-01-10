import os
from pathlib import Path
from typing import List, Tuple

from just.core.config import get_extension_dir, get_command_dir
from just.core.extension.parser import parse_command_structure, Argument
from just.core.extension.utils import search_existing_script
from just.core.extension.validator import sanitize_command_path, validate_command_names
from just.utils.format_utils import docstring


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

    # Sanitize command names for file system compatibility
    sanitized_commands, transformation_notes = sanitize_command_path(commands)

    # Log transformations if any
    if transformation_notes:
        from just import echo
        echo.echo("\nCommand name sanitization applied:")
        for note in transformation_notes:
            echo.echo(f"  - {note}")
        echo.echo("")

    # Validate command names and show warnings
    warnings = validate_command_names(sanitized_commands)
    if warnings:
        from just import echo
        echo.echo("\nCommand validation warnings:")
        for warning in warnings:
            echo.echo(f"  ⚠ {warning}")
        echo.echo("")

    # Calculate paths - extensions for extension commands
    extensions_dir = get_extension_dir()

    script_path = Path(os.path.join(extensions_dir, *sanitized_commands) + '.py')
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

    extensions_dir = get_extension_dir()

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

    extensions_dir = get_extension_dir()
    commands_dir = get_command_dir()

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
                    content = docstring(f"""
                    from just.commands.{commands[0]} import {commands[0]}_cli


                    __all__ = ["{commands[0]}_cli"]
                    """)
                else:
                    # Create new CLI as usual
                    content = docstring(f"""
                    from just import just_cli, create_typer_app


                    {commands[0]}_cli = create_typer_app(name="{commands[0]}")
                    # Add the CLI to the just CLI
                    just_cli.add_typer({commands[0]}_cli)

                    __all__ = ["{commands[0]}_cli"]
                    """)
            else:
                content = docstring(f"""
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
    # Collect all parameters with their default status for sorting
    params_without_default = []
    params_with_default = []

    # Track variable names to avoid duplicates
    used_names = set()

    # Add arguments (skip varargs - they use ctx.args instead)
    for arg in arguments:
        if arg.is_varargs:
            continue  # Varargs are handled via ctx.args, not function parameter
        
        # Ensure unique variable names
        var_name = arg.name
        counter = 1
        while var_name in used_names:
            var_name = f"{arg.name}_{counter}"
            counter += 1
        used_names.add(var_name)

        default_assignment = ""
        has_default = False
        if arg.default_value is not None:
            has_default = True
            # Handle string default values properly
            if isinstance(arg.default_value, str):
                default_assignment = f" = '{arg.default_value}'"
            else:
                default_assignment = f" = {arg.default_value}"
        
        param_str = (
            f"    {var_name}: Annotated[{arg.type.__name__}, typer.Argument(\n"
            f"        help={repr(arg.help)},\n"
            f"        show_default=False\n"
            f"    )]{default_assignment}"
        )
        
        if has_default:
            params_with_default.append(param_str)
        else:
            params_without_default.append(param_str)


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
        has_default = False
        if opt.default_value is not None:
            has_default = True
            # Handle string default values properly
            if isinstance(opt.default_value, str):
                default_assignment = f" = '{opt.default_value}'"
            else:
                default_assignment = f" = {opt.default_value}"
        # Determine if it's a boolean flag option
        elif opt.type.__name__ == 'bool':
            has_default = True
            # Boolean flag without explicit default - treat as True default
            # When True (enabled), keep placeholder; when False (disabled), remove it
            default_assignment = " = True"

        # Build flag arguments - support alias syntax
        if opt.is_append_option:
            # For append options, use variable_name as the user-facing flag
            # Convert underscores back to hyphens for CLI convention
            user_flag = '--' + var_name.replace('_', '-')
            flag_args = repr(user_flag)
        elif opt.flags:  # Use flags property if available (short and/or long)
            flag_args = ', '.join(repr(f) for f in opt.flags)
        else:
            # Fallback to flag name
            flag_args = repr(f'--{flag}')

        param_str = (
            f"    {var_name}: Annotated[{opt.type.__name__}, typer.Option(\n"
            f"        {flag_args},\n"
            f"        help={repr(opt.help)},\n"
            f"        show_default=False\n"
            f"    )]{default_assignment}"
        )
        
        if has_default:
            params_with_default.append(param_str)
        else:
            params_without_default.append(param_str)

    # Combine: params without default first, then params with default
    all_params = params_without_default + params_with_default

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

    # Generate replacements for arguments (skip varargs - handled in template)
    command_replacements = []
    for arg in arguments:
        if arg.is_varargs:
            continue  # Varargs replacement is handled in the template
        var_name = name_mapping[arg.name]
        command_replacements.append(
            f"    command = command.replace({repr(arg.repl_identifier)}, str({var_name}))"
        )


    # Generate replacements for options
    for flag, opt in options.items():
        var_name = name_mapping[opt.name]
        
        # Check if this is an append option (no placeholder, append to command)
        if opt.is_append_option:
            # For append options, add the original flag and value to the command
            original_flag = opt.original_flag
            if opt.type.__name__ == 'bool':
                # Bool append: only add flag when True
                command_replacements.append(
                    f"    if {var_name}:"
                )
                command_replacements.append(
                    f"        command = command + ' {original_flag}'"
                )
            else:
                # Non-bool append: add flag and value if provided
                if opt.default_value is None:
                    # Required option - always append
                    command_replacements.append(
                        f"    command = command + f' {original_flag} {{{var_name}}}'"
                    )
                else:
                    # Optional - only append if different from default
                    command_replacements.append(
                        f"    if {var_name} is not None:"
                    )
                    command_replacements.append(
                        f"        command = command + f' {original_flag} {{{var_name}}}'"
                    )
        else:
            # Normal replacement option or Option Alias
            # Check if this is an Option Alias (identifier starts with '-')
            is_option_alias = opt.repl_identifier.startswith('-')
            
            if opt.type.__name__ == 'bool':
                command_replacements.append(
                    f"    if not {var_name}:"
                )
                command_replacements.append(
                    f"        command = command.replace({repr(opt.repl_identifier)}, '')"
                )
            elif is_option_alias:
                # Option Alias: --text[-m/--msg] means:
                # - If user provides -m value, command gets: --text value
                # - If no value (None or empty), remove --text from command
                if opt.default_value is not None:
                    # Has default value - always include the flag with value
                    command_replacements.append(
                        f"    command = command.replace({repr(opt.repl_identifier)}, f'{opt.repl_identifier} {{{var_name}}}')"
                    )
                else:
                    # No default - conditionally include flag
                    command_replacements.append(
                        f"    if {var_name}:"
                    )
                    command_replacements.append(
                        f"        command = command.replace({repr(opt.repl_identifier)}, f'{opt.repl_identifier} {{{var_name}}}')"
                    )
                    command_replacements.append(
                        f"    else:"
                    )
                    command_replacements.append(
                        f"        command = command.replace({repr(opt.repl_identifier)}, '')"
                    )
            else:
                # Normal placeholder replacement
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
    replacements: str,
    has_varargs: bool = False,
    varargs_identifier: str = "",
    varargs_help: str = ""
) -> str:
    """
    Assemble the complete Typer script content.

    Args:
        custom_command: The original command template
        parent_cmd: Parent command name
        sub_cmd: Sub command name
        signature: Function signature
        replacements: Command replacement logic
        has_varargs: Whether the command has varargs [...]
        varargs_identifier: The placeholder to replace with varargs
        varargs_help: Help message for varargs

    Returns:
        Complete script content
    """
    # Prepare imports based on parent command
    if parent_cmd == "just":
        parent_imports = "from just import just_cli, create_typer_app"
    else:
        parent_imports = f"from just import create_typer_app\nfrom . import {parent_cmd}_cli"

    # Prepare replacements block with proper indentation
    replacements_block = ""
    if replacements:
        lines = []
        for line in replacements.split('\n'):
            if line.strip():
                if not line.startswith('    '):
                    line = '    ' + line
                lines.append(line)
        replacements_block = "\n".join(lines) + "\n"

    # Generate different templates based on varargs mode
    if has_varargs:
        # Varargs mode: use context_settings to capture all unknown args
        script_content = \
f"""import subprocess
import sys

import typer

{parent_imports}


{sub_cmd}_cli = create_typer_app()
# Add the CLI to the parent CLI
{parent_cmd}_cli.add_typer({sub_cmd}_cli)


@{sub_cmd}_cli.command(
    name="{sub_cmd}",
    context_settings={{"allow_extra_args": True, "ignore_unknown_options": True}},
    options_metavar="[ARGS]... [OPTIONS]"
)
def main(
    ctx: typer.Context,
{signature.rstrip()}
):
    \"\"\"
    [ARGS]...  {varargs_help if varargs_help else "Accepts any additional arguments."}
    \"\"\"
    # Capture all unknown arguments (including unknown options like -m)
    args = ctx.args
    command = r\"\"\"
    {custom_command}
    \"\"\".strip()
    command = command.replace({repr(varargs_identifier)}, ' '.join(args))
{replacements_block}
    # Use shell=True for cross-platform compatibility (Windows shell built-ins like echo)
    subprocess.run(command, shell=True)
"""
    else:
        # Standard mode
        script_content = \
f"""import subprocess
import sys
from typing import List

from typing_extensions import Annotated
import typer

{parent_imports}


{sub_cmd}_cli = create_typer_app()
# Add the CLI to the parent CLI
{parent_cmd}_cli.add_typer({sub_cmd}_cli)


@{sub_cmd}_cli.command(name="{sub_cmd}")
def main(
{signature.rstrip()}
):
    command = r\"\"\"
    {custom_command}
    \"\"\".strip()
{replacements_block}
    # Use shell=True for cross-platform compatibility (Windows shell built-ins like echo)
    subprocess.run(command, shell=True)
"""
    return script_content


def generate_extension_script(
    custom_command: str,
    just_commands: List[str],
    overwrite: bool = False
):
    """
    Generate a complete extension script.

    Args:
        custom_command: The original command template
        just_commands: List of command parts
        overwrite: If True, overwrite existing script

    Raises:
        FileExistsError: If the script already exists and overwrite is False
        ValueError: If command structure is invalid
    """
    # Validate input
    validate_command_input(just_commands)

    # Parse command structure
    parsed_commands, arguments, options = parse_command_structure(just_commands)

    # Sanitize command names
    sanitized_commands, transformation_notes = sanitize_command_path(parsed_commands)

    # Log transformations if any
    if transformation_notes:
        from just import echo
        echo.echo("\nCommand name sanitization applied:")
        for note in transformation_notes:
            echo.echo(f"  - {note}")
        echo.echo("")

    # Validate command names and show warnings
    warnings = validate_command_names(sanitized_commands)
    if warnings:
        from just import echo
        echo.echo("\nCommand validation warnings:")
        for warning in warnings:
            echo.echo(f"  ⚠ {warning}")
        echo.echo("")

    # Check if script already exists
    exist, final_expect_script_path = search_existing_script(sanitized_commands)
    if exist and not overwrite:
        raise FileExistsError(f"{final_expect_script_path} already exists")


    # Remove 'just' if it's the first command
    commands = sanitized_commands.copy()
    if commands and commands[0] == 'just':
        commands.pop(0)

    if not commands:
        raise ValueError("No command specified")

    # Ensure directories exist
    ensure_command_directories_exist(sanitized_commands)

    # Generate package init files
    generate_package_init_files(sanitized_commands)

    # Determine command hierarchy
    just_parent_command = f"{commands[-2]}" if len(commands) > 1 else "just"
    just_sub_command = commands[-1]

    # Generate function signature
    signature = generate_function_signature(arguments, options)

    # Generate command replacements
    replacements = generate_command_replacements(arguments, options)

    # Detect varargs
    has_varargs = any(arg.is_varargs for arg in arguments)
    varargs_identifier = ""
    varargs_help = ""
    if has_varargs:
        for arg in arguments:
            if arg.is_varargs:
                varargs_identifier = arg.repl_identifier
                varargs_help = arg.help_msg
                break

    # Assemble final content
    content = assemble_typer_script_content(
        custom_command,
        just_parent_command,
        just_sub_command,
        signature,
        replacements,
        has_varargs=has_varargs,
        varargs_identifier=varargs_identifier,
        varargs_help=varargs_help
    )

    # Write the script file
    script_path = Path(final_expect_script_path)
    script_path.parent.mkdir(parents=True, exist_ok=True)

    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(content)

    # Return script path and command list for caller
    return script_path, commands