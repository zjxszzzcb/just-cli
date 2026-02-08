import typer
import just
from typing_extensions import Annotated

@just.installer(check="zed --version")
def install_zed(
    version: Annotated[str, just.Option("--version", "-v", help="Specific version to install")] = "",
    channel: Annotated[str, just.Option("--channel", "-c", help="Release channel (stable/preview)")] = "stable"
):
    """
    Install Zed editor - a high-performance, multiplayer code editor.

    Supports:
    - Windows (winget, script)
    - macOS (brew, script)
    - Linux (flatpak, script)
    """
    # Validate channel
    if channel not in ["stable", "preview"]:
        just.echo.error(f"Invalid channel: {channel}. Must be 'stable' or 'preview'")
        raise typer.Exit(code=1)

    # Platform-specific installation
    if just.system.platform == "windows":
        _install_zed_windows(version, channel)
    elif just.system.platform == "darwin":
        _install_zed_macos(version, channel)
    elif just.system.platform == "linux":
        _install_zed_linux(version, channel)
    else:
        raise NotImplementedError(f"Unsupported platform: {just.system.platform}")


def _install_zed_windows(version: str, channel: str):
    """Install Zed on Windows."""
    if just.system.pms.winget.is_available():
        just.echo.info("Installing Zed via winget...")
        cmd = "winget install -e --id ZedEditor.Zed"
        if channel == "preview":
            cmd += " --override '/CHANNEL=preview'"
        just.execute_commands(cmd)
    else:
        _install_zed_via_script(version, channel)


def _install_zed_macos(version: str, channel: str):
    """Install Zed on macOS."""
    if just.system.pms.brew.is_available():
        just.echo.info("Installing Zed via Homebrew...")
        # Homebrew uses cask for Zed
        cask_name = "zed-preview" if channel == "preview" else "zed"
        just.execute_commands(f"brew install --cask {cask_name}")
    else:
        _install_zed_via_script(version, channel)


def _install_zed_linux(version: str, channel: str):
    """Install Zed on Linux."""
    # Check for flatpak first
    import shutil
    if shutil.which("flatpak"):
        just.echo.info("Installing Zed via flatpak...")
        app_id = "dev.zed.Zed" if channel == "stable" else "dev.zed.Zed.Preview"
        just.execute_commands(f"flatpak install flathub {app_id}")
    else:
        _install_zed_via_script(version, channel)


def _install_zed_via_script(version: str, channel: str):
    """Install Zed using the official installation script."""
    just.echo.info("Installing Zed via official script...")

    # Build environment variables for the script
    env_vars = {}
    if version:
        env_vars["ZED_VERSION"] = version
    if channel:
        env_vars["ZED_CHANNEL"] = channel

    # Determine script URL based on platform
    if just.system.platform == "windows":
        script_url = "https://zed.dev/install.ps1"
        script_file = "install-zed.ps1"
        execute_cmd = f"powershell -ExecutionPolicy Bypass -File {script_file}"
    else:
        script_url = "https://zed.dev/install.sh"
        script_file = "install-zed.sh"
        execute_cmd = f"bash {script_file}"

    # Download the script
    just.download_with_resume(
        script_url,
        output_file=script_file
    )

    # Execute the script with environment variables if needed
    if env_vars:
        import os
        # Create a wrapper script that sets environment variables
        if just.system.platform == "windows":
            env_script = "install-zed-wrapper.ps1"
            with open(env_script, "w") as f:
                f.write("$env:ZED_VERSION = '" + env_vars.get("ZED_VERSION", "") + "'\n")
                f.write("$env:ZED_CHANNEL = '" + env_vars.get("ZED_CHANNEL", "stable") + "'\n")
                f.write(f".\\{script_file}\n")
            execute_cmd = f"powershell -ExecutionPolicy Bypass -File {env_script}"
        else:
            env_script = "install-zed-wrapper.sh"
            with open(env_script, "w") as f:
                if version:
                    f.write(f"export ZED_VERSION=\"{version}\"\n")
                if channel:
                    f.write(f"export ZED_CHANNEL=\"{channel}\"\n")
                f.write(f"bash {script_file}\n")
            execute_cmd = f"bash {env_script}"

    just.execute_commands(execute_cmd)

    # Clean up downloaded scripts
    just.execute_commands(f"just rm {script_file}")
    if env_vars:
        wrapper_script = "install-zed-wrapper.ps1" if just.system.platform == "windows" else "install-zed-wrapper.sh"
        just.execute_commands(f"just rm {wrapper_script}")
