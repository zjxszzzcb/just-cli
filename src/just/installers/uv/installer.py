import just


@just.installer(check="uv --version")
def install_uv():
    """Install uv Python package manager."""

    # macOS: try Homebrew first, then official installer
    if just.system.platform == "darwin":
        if just.system.pms.brew.is_available():
            just.execute_commands("brew install uv")
        else:
            # Official installer
            just.execute_commands("curl -LsSf https://astral.sh/uv/install.sh | sh")

    # Windows: try winget first, then official installer
    elif just.system.platform == "windows":
        if just.system.pms.winget.is_available():
            just.execute_commands("winget install astral-sh.uv")
        else:
            # Official PowerShell installer
            just.execute_commands(
                'powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"'
            )

    # Linux: official installer script
    elif just.system.platform == "linux":
        just.execute_commands("curl -LsSf https://astral.sh/uv/install.sh | sh")

    else:
        raise NotImplementedError(f"uv is not supported on {just.system.platform}")

    just.echo.success("uv installed successfully.")
