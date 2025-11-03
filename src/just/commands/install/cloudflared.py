import os
import platform

from just import capture_exception, echo
from just.utils import execute_command

from . import install_cli


def check_cloudflared_exist():
    """
    Check if cloudflared is installed.
    """
    exit_code, output = execute_command("cloudflared -v", capture_output=True)
    if exit_code == 0:
        return True
    else:
        return False


@install_cli.command(name="cloudflare")
@capture_exception
def install_cloudflared():
    """
    Install Cloudflare toolkit.
    """
    if check_cloudflared_exist():
        echo.green("Cloudflare is already installed")
        return

    if platform.system() == "Windows":
        execute_command('winget install --id Cloudflare.cloudflared')
    else:
        msg = f"The installation of 'cloudflare' on the '{platform.system()}' platform has not been implemented."
        echo.error(msg)
        return

    if check_cloudflared_exist():
        echo.green("Successfully installed Cloudflare")
    else:
        echo.error("Failed to install Cloudflare")
