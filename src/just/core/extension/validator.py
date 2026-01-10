import re
from typing import List, Tuple


def sanitize_command_name(command: str) -> Tuple[str, str]:
    """
    Sanitize a command name to be a valid Python identifier and file name.

    Args:
        command: The raw command name to sanitize

    Returns:
        Tuple of (sanitized_name, transformation_note)
        - sanitized_name: Safe version for use as variable/filename
        - transformation_note: Human-readable description of changes made
    """
    original = command

    # Check if it's a pure numeric command
    if command.isdigit():
        sanitized = f"num_{command}"
        return sanitized, "Added 'num_' prefix to numeric command"

    # Replace special characters with underscores
    # Allow: alphanumeric, underscore, dash (for readability in some contexts)
    # But for Python identifiers, we need to be more strict
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', command)

    # Remove consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)

    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')

    # Ensure it doesn't start with a number
    if sanitized and sanitized[0].isdigit():
        sanitized = f"num_{sanitized}"

    # If still empty or invalid, provide fallback
    if not sanitized or not sanitized.replace('_', ''):
        sanitized = f"cmd_{hash(original) % 10000}"

    # Generate transformation note
    if sanitized != original:
        transformations = []
        if original.isdigit():
            transformations.append("numeric prefix added")
        if '_' in sanitized and any(c in original for c in '-/.'):
            transformations.append("special characters replaced with underscores")
        note = ", ".join(transformations)
        return sanitized, f"Command sanitized ({note})"

    return sanitized, "No changes needed"


def sanitize_command_path(commands: List[str]) -> Tuple[List[str], List[str]]:
    """
    Sanitize a list of command parts for use in file paths.

    Args:
        commands: List of command parts (e.g., ['docker', 'inspect-container'])

    Returns:
        Tuple of (sanitized_commands, transformation_notes)
    """
    sanitized = []
    notes = []

    for cmd in commands:
        clean_cmd, note = sanitize_command_name(cmd)
        if clean_cmd != cmd:
            notes.append(f"'{cmd}' → '{clean_cmd}'")
        sanitized.append(clean_cmd)

    return sanitized, notes


def validate_command_names(commands: List[str]) -> List[str]:
    """
    Validate that command names follow naming conventions.

    Returns:
        List of warning messages (empty if all valid)
    """
    warnings = []

    # Python reserved keywords
    python_keywords = {
        'False', 'None', 'True', '__peg_parser__', 'and', 'as', 'assert',
        'async', 'await', 'break', 'class', 'continue', 'def', 'del',
        'elif', 'else', 'except', 'finally', 'for', 'from', 'global',
        'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or',
        'pass', 'raise', 'return', 'try', 'while', 'with', 'yield', 'int',
        'str', 'float', 'bool', 'list', 'dict', 'tuple', 'set'
    }

    for cmd in commands:
        # Check for reserved Python keywords
        if cmd in python_keywords:
            warnings.append(f"Command '{cmd}' is a Python keyword and may cause issues")

        # Check for very long names
        if len(cmd) > 50:
            warnings.append(f"Command '{cmd}' is very long ({len(cmd)} > 50 chars)")

        # Check for duplicate consecutive underscores
        if '__' in cmd:
            warnings.append(f"Command '{cmd}' contains consecutive underscores (will be normalized)")

        # Check for dot notation (should use underscores instead)
        if '.' in cmd:
            warnings.append(f"Command '{cmd}' uses dot notation (will be converted to underscores)")

        # Check for path traversal patterns
        if '..' in cmd or cmd.startswith('/') or cmd.startswith('\\'):
            warnings.append(f"Command '{cmd}' contains path traversal patterns (not recommended)")

    return warnings