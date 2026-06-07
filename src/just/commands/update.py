import subprocess
import sys

from just import Annotated, just_cli, capture_exception
from just.utils import echo
from just.utils.typer_utils import detect_install_method, get_just_version


@just_cli.command(name="update")
@capture_exception
def update_command() -> None:
    """
    Update just-cli to the latest version.

    Automatically detects the installation method and runs the
    corresponding update command.
    """
    method = detect_install_method()
    current = get_just_version()
    echo.info(f"Current version: {current}")

    if method == "uv":
        echo.info("Detected uv tool installation, updating...")
        result = subprocess.run(
            ["uv", "tool", "install", "just-cli", "-U"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            new_version = get_just_version()
            echo.info(f"Updated to {new_version}")
        else:
            echo.error(f"Update failed: {result.stderr.strip()}")

    elif method == "pip":
        echo.info("Detected pip installation, updating...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "just-cli", "-U"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            new_version = get_just_version()
            echo.info(f"Updated to {new_version}")
        else:
            echo.error(f"Update failed: {result.stderr.strip()}")

    else:
        echo.error("Cannot determine installation method.")
        echo.info("Please update manually:")
        echo.info("  uv tool install just-cli -U")
        echo.info("  pip install just-cli -U")
