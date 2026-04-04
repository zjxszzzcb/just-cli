import just
from just.core.installer import BashScriptInstaller


@just.installer(check="uv --version")
def install_uv():
    """Install uv Python package manager via official installer script."""

    if just.system.platform == "darwin":
        # macOS: official installer
        BashScriptInstaller(
            commands="curl -LsSf https://astral.sh/uv/install.sh | sh"
        ).run()

    elif just.system.platform == "windows":
        # Windows: official PowerShell installer
        BashScriptInstaller(
            commands='powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"'
        ).run()

    elif just.system.platform == "linux":
        # Linux: official installer
        BashScriptInstaller(
            commands="curl -LsSf https://astral.sh/uv/install.sh | sh"
        ).run()

    else:
        raise NotImplementedError(f"uv is not supported on {just.system.platform}")

    just.echo.success("uv installed successfully.")
