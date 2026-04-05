"""Common utility functions for installers."""

import os
from pathlib import Path

from just.utils import echo
from just.utils.file_utils import symlink


def make_executable(file_path: Path) -> None:
    """Make file executable on Unix systems."""
    if os.name != "nt":
        import stat
        st = os.stat(file_path)
        os.chmod(file_path, st.st_mode | stat.S_IEXEC)
        echo.debug(f"Made executable: {file_path}")


def create_symlink_or_wrapper(target: Path, link_dir: Path, link_name: str) -> None:
    """
    Create symlink on Unix or wrapper script on Windows.

    Args:
        target: Target file/directory path
        link_dir: Directory where link/wrapper will be created
        link_name: Name of the link/wrapper
    """
    # Ensure link directory exists
    link_dir.mkdir(parents=True, exist_ok=True)

    link_path = link_dir / link_name

    # Remove existing link if it exists
    if link_path.exists() or link_path.is_symlink():
        link_path.unlink()

    if os.name == "nt":
        _create_windows_wrapper(target, link_path)
    else:
        _create_unix_symlink(target, link_path)


def _create_unix_symlink(target: Path, link_path: Path) -> None:
    """Create symlink on Unix systems."""
    symlink(str(target), str(link_path))
    echo.info(f"Created symlink: {link_path.name} -> {target}")


def _create_windows_wrapper(target: Path, wrapper_path: Path) -> None:
    """Create wrapper batch script on Windows."""
    # Remove .exe extension if present for wrapper name
    wrapper_name = wrapper_path.stem
    wrapper_path = wrapper_path.parent / f"{wrapper_name}.bat"

    # Create batch wrapper script
    wrapper_content = f'@echo off\r\n"{target}" %*\r\n'

    with open(wrapper_path, "w") as f:
        f.write(wrapper_content)

    echo.info(f"Created wrapper script: {wrapper_name}.bat -> {target}")


def check_path_included(bin_dir: Path) -> None:
    """
    Check if bin directory is in PATH and warn if not.

    Args:
        bin_dir: Bin directory path to check
    """
    path_env = os.environ.get("PATH", "")
    bin_dir_str = str(bin_dir.resolve())

    if bin_dir_str not in path_env.split(os.pathsep):
        echo.warning("")
        echo.warning(f"{bin_dir} is not in your PATH")
        echo.info("Add the following to your shell config:")
        echo.info("")

        # Detect shell and provide instructions
        shell = os.environ.get("SHELL", "")

        if "bash" in shell:
            echo.info(
                f"  echo 'export PATH=\"$HOME/.just/bin:$PATH\"' >> ~/.bashrc"
            )
            echo.info(f"  source ~/.bashrc")
        elif "zsh" in shell:
            echo.info(f"  echo 'export PATH=\"$HOME/.just/bin:$PATH\"' >> ~/.zshrc")
            echo.info(f"  source ~/.zshrc")
        elif "fish" in shell:
            echo.info(f"  fish_add_path ~/.just/bin")
        elif os.name == "nt":
            echo.info(f'  setx PATH "%PATH%;%USERPROFILE%\\.just\\bin"')
        else:
            echo.info(f'  export PATH="$HOME/.just/bin:$PATH"')

        echo.info("")
