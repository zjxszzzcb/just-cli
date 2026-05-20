import just
from just.core.installer import BashScriptInstaller, PowerShellInstaller


@just.installer(check="kimi --version")
def install_kimi():
    """Install Kimi Code CLI by Moonshot AI."""

    if just.system.platform in ("linux", "darwin"):
        BashScriptInstaller(
            script_url="https://code.kimi.com/install.sh",
            name="kimi",
        ).run()

    elif just.system.platform == "windows":
        PowerShellInstaller(
            script_url="https://code.kimi.com/install.ps1",
            name="kimi",
        ).run()

    else:
        raise NotImplementedError(
            f"Kimi Code CLI is not supported on {just.system.platform}."
        )
