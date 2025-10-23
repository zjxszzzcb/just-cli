import os
import platform
import subprocess

from just import echo, update_env_file, capture_exception
from .entry import install_cli


@install_cli.command(name="edit", help="Install Microsoft Edit.")
@capture_exception
def install_microsoft_edit():
    output = subprocess.run(['edit', '-v'], capture_output=True, text=True)
    if output.returncode == 0:
        echo.green("Microsoft Edit is already installed")
        update_env_file("JUST_EDIT_USE_TOOL", "edit")
    elif platform.system() == "Windows":
        cmd = "winget install Microsoft.Edit"
        echo.echo(f"> {cmd}")
        os.system(cmd)
        update_env_file("JUST_EDIT_USE_TOOL", "edit")
    else:
        msg = f"The installation of 'edit' on the '{platform.system()}' platform has not been implemented."
        echo.error(msg)
