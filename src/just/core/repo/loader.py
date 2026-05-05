"""Dynamic loader for repo commands and installers."""
import importlib
import os
import sys

from pathlib import Path

from just.core.config import get_repo_dir
from just.utils import echo


def load_repos_dynamically() -> None:
    """Scan ~/.just/repos/ and load commands + installers from each repo."""
    repo_base = get_repo_dir()
    if not repo_base.exists():
        return

    for item in sorted(repo_base.iterdir()):
        if not item.is_dir() or item.name.startswith("."):
            continue
        if not (item / ".git").exists():
            continue

        _load_repo_commands(item)
        _load_repo_installers(item)


def _load_repo_commands(repo_dir: Path) -> None:
    """Import all Python files in repo's commands/ directory."""
    commands_dir = repo_dir / "commands"
    if not commands_dir.is_dir():
        return

    # Add repo root to sys.path so imports work
    repo_root = str(repo_dir)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    for root, dirs, files in os.walk(commands_dir):
        for file in files:
            if not file.startswith("_") and file.endswith(".py"):
                try:
                    rel_path = Path(root).relative_to(repo_dir)
                    module_name = ".".join(rel_path.parts) + f".{Path(file).stem}"
                    importlib.import_module(module_name)
                except Exception as e:
                    echo.warning(
                        f"Failed to load command from repo "
                        f"'{repo_dir.name}/{file}': {e}"
                    )


def _load_repo_installers(repo_dir: Path) -> None:
    """Register repo's installers/ directory as an installer source."""
    installers_dir = repo_dir / "installers"
    if not installers_dir.is_dir():
        return

    # Append to JUST_INSTALLER_SOURCES so install_package() can find them
    from just import config
    installer_path = str(installers_dir)
    if installer_path not in config.JUST_INSTALLER_SOURCES:
        config.JUST_INSTALLER_SOURCES.append(installer_path)
