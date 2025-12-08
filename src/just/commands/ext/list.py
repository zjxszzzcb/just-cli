import os
from pathlib import Path
from typing import Dict, List

import typer

from just.utils.echo_utils import red, green, yellow, blue, cyan, echo
from just.core.config import get_extension_dir


def find_extensions(extensions_dir: Path) -> Dict[str, List[str]]:
    """
    Find all extensions in the extensions directory.

    Returns:
        Dictionary mapping command paths to their file paths
    """
    extensions = {}

    # Walk through the extensions directory
    for root, dirs, files in os.walk(extensions_dir):
        root_path = Path(root)

        # Skip __pycache__ directories
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')

        # Look for Python files (but not __init__.py)
        py_files = [f for f in files if f.endswith('.py') and f != '__init__.py']

        if py_files:
            # Get the relative path from extensions_dir
            try:
                rel_path = root_path.relative_to(extensions_dir)
                # Convert to command path (parts of the path)
                command_parts = list(rel_path.parts)

                for py_file in py_files:
                    # Remove .py extension
                    file_stem = py_file[:-3]
                    # Combine path parts with the file stem
                    command_path = tuple(command_parts + [file_stem])
                    full_path = root_path / py_file

                    # Store the mapping
                    extensions[' '.join(command_path)] = str(full_path)
            except ValueError:
                # Path is not relative, skip
                continue

    return extensions


def print_tree_structure(extensions: Dict[str, List[str]], max_width: int = 80) -> None:
    """
    Print the extensions in a tree structure.

    Args:
        extensions: Dictionary mapping command paths to file paths
        max_width: Maximum width for the tree display
    """
    if not extensions:
        yellow("No extensions found.")
        echo()
        cyan("Tip: Create an extension using 'just ext add'")
        return

    cyan("\nJust Extensions Tree:")
    echo("=" * max_width)

    # Sort commands for consistent output
    sorted_commands = sorted(extensions.keys())

    # Track which top-level commands we've seen
    top_level_commands = set()

    for command in sorted_commands:
        parts = command.split()

        if len(parts) == 1:
            # Top-level command
            if parts[0] not in top_level_commands:
                green(f"\n📦 {parts[0]}")
                top_level_commands.add(parts[0])

        elif len(parts) == 2:
            # Two-level command (e.g., docker ip)
            top_cmd = parts[0]
            sub_cmd = parts[1]
            file_path = extensions[command]

            # Check if we need to print the top-level command again
            if top_cmd not in top_level_commands:
                green(f"\n📦 {top_cmd}")
                top_level_commands.add(top_cmd)

            green(f"  └── {sub_cmd}")

            # Show file info in a compact format
            rel_path = Path(file_path).relative_to(get_extension_dir())
            echo(f"      📄 {rel_path}")

        else:
            # Multi-level command (e.g., api v1 users get)
            all_parts = parts
            top_cmd = all_parts[0]

            # Check if we need to print the top-level command
            if top_cmd not in top_level_commands:
                green(f"\n📦 {top_cmd}")

            # Print nested structure
            indent = "  "
            for i, part in enumerate(all_parts[1:], 1):
                connector = "└──" if i == len(all_parts[1:]) else "├──"
                green(f"{indent}{connector} {part}")
                indent += "    " if i == len(all_parts[1:]) else "│   "

            # Show file info
            rel_path = Path(extensions[command]).relative_to(get_extension_dir())
            echo(f"{indent}    📄 {rel_path}")

    echo()
    echo("=" * max_width)
    cyan(f"\nTotal: {len(extensions)} extension(s) found")


def list_extensions():
    """
    List all just extensions in a tree structure.
    """
    extensions_dir = get_extension_dir()

    if not extensions_dir.exists():
        yellow("Extensions directory not found.")
        echo(f"Location: {extensions_dir}")
        echo()
        cyan("Tip: Create an extension using 'just ext add'")
        raise typer.Exit(code=0)

    # Find all extensions
    extensions = find_extensions(extensions_dir)

    # Print the tree structure
    print_tree_structure(extensions)