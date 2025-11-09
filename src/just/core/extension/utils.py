import os
import re
from pathlib import Path
from typing import Any, List, Tuple

from just.core.config import get_command_dir, get_extension_dir


TYPES = {
    'str': str,
    'int': int,
    'float': float,
    'bool': bool
}


def search_existing_script(just_commands: List[str]) -> Tuple[bool, str]:
    """
    Search for an existing script file.

    Args:
        just_commands: List of command parts

    Returns:
        Tuple of (exists, file_path)
    """
    commands_dir = get_command_dir()
    extensions_dir = get_extension_dir()

    # Remove 'just' if it's the first command
    commands = just_commands.copy()
    if commands and commands[0] == 'just':
        commands.pop(0)

    if not commands:
        raise ValueError("No command specified")

    # Check in commands directory
    script_path = Path(os.path.join(commands_dir, *commands) + '.py')
    if script_path.exists():
        return True, script_path.as_posix()

    # Check in extensions directory
    script_path = Path(os.path.join(extensions_dir, *commands) + '.py')
    return script_path.exists(), script_path.as_posix()


def process_parameter_annotation(annotation: str) -> Tuple[str, type, Any, str]:
    """
    Process a parameter annotation string.

    Args:
        annotation: Annotation string like "name:str#help message" or "name:str=default#help message"

    Returns:
        Tuple of (name, type, default_value, help_message)
    """
    help_msg = ""
    default_value = None
    variable_type = 'str'

    # Extract help message
    if '#' in annotation:
        annotation, help_msg = annotation.split('#', maxsplit=1)

    # Extract default value
    if '=' in annotation:
        annotation, default_value = annotation.split('=', maxsplit=1)

    # Extract type and name
    if ':' in annotation:
        variable_name, variable_type = annotation.split(':', maxsplit=1)
    else:
        variable_name = annotation

    # Convert type string to actual type
    type_obj = TYPES.get(variable_type, str)

    # Convert default value to appropriate type
    if default_value is not None:
        if variable_type == 'int':
            try:
                default_value = int(default_value)
            except ValueError:
                pass  # Keep as string if conversion fails
        elif variable_type == 'float':
            try:
                default_value = float(default_value)
            except ValueError:
                pass  # Keep as string if conversion fails
        elif variable_type == 'bool':
            default_value = default_value.lower() in ('true', '1', 'yes', 'on')

    return variable_name, type_obj, default_value, help_msg


def convert_default_value(value: str, type_hint: str) -> Any:
    """
    Convert a default value string to the appropriate type.

    Args:
        value: Default value as string
        type_hint: Type hint string

    Returns:
        Converted value
    """
    if value is None:
        return None

    if type_hint == 'int':
        try:
            return int(value)
        except ValueError:
            return value  # Return as string if conversion fails
    elif type_hint == 'float':
        try:
            return float(value)
        except ValueError:
            return value  # Return as string if conversion fails
    elif type_hint == 'bool':
        return value.lower() in ('true', '1', 'yes', 'on')
    else:
        return value


def split_command_line(command_line: str) -> List[str]:
    """
    Split JUST CLI command line while preserving annotations with spaces.

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
    return re.findall(r'\S*\[.*?]|\S+', command_line.strip())