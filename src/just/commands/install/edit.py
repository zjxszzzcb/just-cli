import platform

from just import config, echo, update_env_file, capture_exception
from just.utils import execute_command

from . import install_cli


def check_microsoft_edit_exist():
    """
    Check if Microsoft Edit is installed.
    """
    exit_code, output = execute_command("edit -v", capture_output=True)
    if exit_code == 0:
        return True
    else:
        return False


@install_cli.command(name="edit")
@capture_exception
def install_microsoft_edit():
    """
    Install Microsoft Edit.
    """
    if check_microsoft_edit_exist():
        echo.green("Microsoft Edit is already installed")
        update_env_file("JUST_EDIT_USE_TOOL", "edit")
        return

    if platform.system() == "Windows":
        execute_command("winget install Microsoft.Edit")
    else:
        msg = f"The installation of 'edit' on the '{platform.system()}' platform has not been implemented."
        echo.error(msg)
        return

    if check_microsoft_edit_exist():
        echo.green("Successfully installed Microsoft Edit")
        update_env_file("JUST_EDIT_USE_TOOL", "edit")
    else:
        echo.error("Failed to install Microsoft Edit")
