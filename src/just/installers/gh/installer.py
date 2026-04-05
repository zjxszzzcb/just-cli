import just


@just.installer(check="gh --version")
def install_gh():
    """Install GitHub CLI (gh)."""

    if just.system.platform == "darwin":
        if just.system.pms.brew.is_available():
            just.execute_commands("brew install gh")
        else:
            raise NotImplementedError(
                "Homebrew is required to install gh on macOS.\n"
                "Visit: https://github.com/cli/cli/releases"
            )

    elif just.system.platform == "windows":
        if just.system.pms.winget.is_available():
            just.execute_commands("winget install --id GitHub.cli")
        else:
            raise NotImplementedError(
                "winget or chocolatey is required to install gh on Windows.\n"
                "Visit: https://github.com/cli/cli/releases"
            )

    elif just.system.platform == "linux":
        installed = False

        if just.system.pms.apt.is_available():
            try:
                just.execute_commands([
                    "curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg",
                    "echo 'deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main' | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null",
                    "sudo apt update && sudo apt install gh"
                ])
                installed = True
            except Exception:
                pass

        if not installed:
            raise NotImplementedError(
                "Failed to install gh via package manager.\n"
                "Visit: https://github.com/cli/cli/releases for manual installation."
            )

    else:
        raise NotImplementedError(f"gh is not supported on {just.system.platform}")

    just.echo.success("GitHub CLI (gh) installed successfully.")
