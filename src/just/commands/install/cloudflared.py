import os
import platform

from just import capture_exception, echo
from . import install_cli


@install_cli.command(name="cloudflare", help="Install Cloudflare toolkit.")
@capture_exception
def install_cloudflared():
    if platform.system() == "Windows":
        os.system('winget install --id Cloudflare.cloudflared')
    else:
        msg = f"The installation of 'cloudflare' on the '{platform.system()}' platform has not been implemented."
        echo.error(msg)
