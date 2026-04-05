import just


@just.installer(check="brew --version")
def install_brew():
    """
    Install Homebrew package manager on macOS and Linux.

    The official Homebrew installer script will be downloaded and executed.
    """
    if just.system.platform in ("darwin", "linux"):
        just.BashScriptInstaller(
            script_url="https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh"
        ).run()
    else:
        raise NotImplementedError(
            f"Homebrew is not supported on {just.system.platform}."
        )
