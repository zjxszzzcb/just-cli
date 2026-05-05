"""Repo management operations."""
import subprocess
from pathlib import Path
from typing import List, Optional

from just.core.config import ensure_repo_dir_exists, get_repo_dir
from just.utils import echo


def add_repo(name: str, url: str) -> Path:
    """Clone a git repo to ~/.just/repos/<name>/."""
    repo_dir = get_repo_dir() / name
    if repo_dir.exists():
        raise ValueError(f"Repo '{name}' already exists at {repo_dir}")

    ensure_repo_dir_exists()
    echo.info(f"Cloning repo '{name}' from {url}...")

    result = subprocess.run(
        ["git", "clone", url, str(repo_dir)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        # Clean up partial clone on failure
        if repo_dir.exists():
            import shutil
            shutil.rmtree(repo_dir, ignore_errors=True)
        raise RuntimeError(f"Failed to clone repo: {result.stderr.strip()}")

    echo.success(f"Repo '{name}' added successfully.")
    return repo_dir


def remove_repo(name: str) -> None:
    """Remove a repo by name."""
    repo_dir = get_repo_dir() / name
    if not repo_dir.exists():
        raise ValueError(f"Repo '{name}' not found")

    import shutil
    shutil.rmtree(repo_dir)
    echo.success(f"Repo '{name}' removed.")


def list_repos() -> List[dict]:
    """List all installed repos with metadata."""
    repo_base = get_repo_dir()
    if not repo_base.exists():
        return []

    repos = []
    for item in sorted(repo_base.iterdir()):
        if not item.is_dir() or item.name.startswith("."):
            continue
        if not (item / ".git").exists():
            continue
        info = _get_repo_info(item)
        repos.append(info)

    return repos


def update_repo(name: Optional[str] = None) -> None:
    """Pull latest changes for a specific repo or all repos."""
    if name:
        repo_dir = get_repo_dir() / name
        if not repo_dir.exists():
            raise ValueError(f"Repo '{name}' not found")
        _pull_repo(repo_dir)
        return

    repo_base = get_repo_dir()
    if not repo_base.exists():
        echo.info("No repos installed.")
        return

    for item in sorted(repo_base.iterdir()):
        if not item.is_dir() or item.name.startswith("."):
            continue
        if not (item / ".git").exists():
            continue
        _pull_repo(item)


def _pull_repo(repo_dir: Path) -> None:
    """Git pull a single repo."""
    name = repo_dir.name
    echo.info(f"Updating repo '{name}'...")

    result = subprocess.run(
        ["git", "pull"],
        cwd=str(repo_dir),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        echo.error(f"Failed to update '{name}': {result.stderr.strip()}")
        return

    output = result.stdout.strip()
    if "Already up to date" in output or "Already up-to-date" in output:
        echo.info(f"  '{name}' is already up to date.")
    else:
        echo.success(f"  '{name}' updated.")


def _get_repo_info(repo_dir: Path) -> dict:
    """Extract metadata from a repo directory."""
    name = repo_dir.name

    url = _git_command(repo_dir, ["git", "remote", "get-url", "origin"])
    branch = _git_command(repo_dir, ["git", "rev-parse", "--abbrev-ref", "HEAD"])
    commit = _git_command(repo_dir, ["git", "rev-parse", "--short", "HEAD"])

    return {
        "name": name,
        "path": repo_dir,
        "url": url,
        "branch": branch,
        "commit": commit,
        "has_commands": (repo_dir / "commands").is_dir(),
        "has_installers": (repo_dir / "installers").is_dir(),
    }


def _git_command(repo_dir: Path, cmd: List[str]) -> str:
    """Run a git command in a repo directory and return stdout."""
    result = subprocess.run(
        cmd,
        cwd=str(repo_dir),
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else ""
