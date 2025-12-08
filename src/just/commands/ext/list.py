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


def build_tree_structure(extensions: Dict[str, str]) -> Dict:
    """
    Build a hierarchical tree structure from flat command paths.
    
    Args:
        extensions: Dictionary mapping command paths to file paths
        
    Returns:
        Nested dictionary representing the tree structure
    """
    tree = {}
    for command, file_path in extensions.items():
        parts = command.split()
        current = tree
        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]
        current['__file__'] = file_path
    return tree


def print_tree_node(node: Dict, prefix: str = "", is_last: bool = True):
    """
    Recursively print a tree node.
    
    Args:
        node: Tree node dictionary
        prefix: Current line prefix for indentation
        is_last: Whether this is the last child
    """
    items = [(k, v) for k, v in node.items() if k != '__file__']
    
    for i, (key, value) in enumerate(items):
        is_last_item = (i == len(items) - 1)
        connector = "└──" if is_last_item else "├──"
        
        has_children = any(k != '__file__' for k in value.keys())
        is_command = '__file__' in value
        
        if has_children:
            echo(f"{prefix}{connector} ", end='')
            yellow(key)
        elif is_command:
            echo(f"{prefix}{connector} ", end='')
            blue(key)
        else:
            echo(f"{prefix}{connector} {key}")
        
        if has_children:
            extension = "    " if is_last_item else "│   "
            print_tree_node(value, prefix + extension, is_last_item)


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

    tree = build_tree_structure(extensions)
    
    top_commands = sorted(tree.keys())
    for top_cmd in top_commands:
        echo("\n📦 ", end='')
        yellow(top_cmd)
        print_tree_node(tree[top_cmd], prefix="  ", is_last=True)

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