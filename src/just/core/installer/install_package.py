"""Package installation utilities."""

from pathlib import Path
from typing import List, Optional

import typer

from just import config
from just.core.system_probe import get_arch, get_platform, get_distro_name_version
from just.core.config import get_basic_installer_dir

from .package_info import PackageInfo
from .source import fetch_installer_source


def install_package(package_name: str, additional_args: Optional[List[str]] = None):
    arch = get_arch()
    platform = get_platform()
    distro, distro_version = get_distro_name_version(platform)
    package_info = PackageInfo(
        name=package_name,
        platform=platform,
        arch=arch,
        distro=distro,
        distro_version=distro_version,
    )

    installer_sources = config.JUST_INSTALLER_SOURCES
    installer_sources.insert(0, str(get_basic_installer_dir()))

    for source in installer_sources:
        source_instance = fetch_installer_source(source)
        installer = source_instance.get_installer(package_info)
        if installer:
            break
    else:
        raise Exception(f"No installer script found for {package_name}")

    app = typer.Typer()

    # Check if already installed
    check_cmd = getattr(installer, "_check_command", None)
    if check_cmd:
        from just.utils import execute_command, echo
        import shlex
        import shutil

        # Extract command name from check command (e.g., "opencode --version" -> "opencode")
        cmd_parts = shlex.split(check_cmd)
        cmd_name = cmd_parts[0] if cmd_parts else check_cmd

        # Check if command exists before executing (follows probe_tool pattern)
        if shutil.which(cmd_name):
            exit_code, _ = execute_command(check_cmd, capture_output=True)
            if exit_code == 0:
                echo.success(f"{package_name} is already installed.")
                return
        # If command doesn't exist, silently proceed with installation

    app.command()(installer)
    app(additional_args)


def list_available_installers() -> List[dict]:
    """
    List all available installers from the built-in installer directory.

    Returns:
        List of dicts with 'name' and 'description' keys.
    """
    installers = []
    installer_dir = get_basic_installer_dir()

    if not installer_dir.exists():
        return installers

    for item in installer_dir.iterdir():
        if not item.is_dir():
            continue

        # Skip __pycache__ and other hidden directories
        if item.name.startswith("_") or item.name.startswith("."):
            continue

        installer_file = item / "installer.py"
        if not installer_file.exists():
            continue

        # Extract description from docstring
        description = _extract_installer_description(installer_file)
        installers.append({"name": item.name, "description": description})

    # Sort by name
    installers.sort(key=lambda x: x["name"])
    return installers


def _extract_installer_description(installer_file: Path) -> str:
    """
    Extract description from installer's docstring.

    Looks for the @just.installer decorated function and extracts its docstring.
    """
    try:
        content = installer_file.read_text(encoding="utf-8")

        import re

        # Find @just.installer decorator position
        decorator_match = re.search(r"@just\.installer", content)
        if not decorator_match:
            return "No description available"

        # Search for docstring after the decorator
        # Look for triple-quoted strings after the function definition
        after_decorator = content[decorator_match.start() :]

        # Match docstring: find """ or ''' followed by content
        docstring_pattern = r'(?:"""|\'\'\')([\s\S]*?)(?:"""|\'\'\')'
        docstring_match = re.search(docstring_pattern, after_decorator)

        if docstring_match:
            docstring = docstring_match.group(1).strip()
            # Get first line of docstring
            first_line = docstring.split("\n")[0].strip()
            return first_line if first_line else "No description available"

        return "No description available"
    except Exception:
        return "No description available"
