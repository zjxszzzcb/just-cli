import just


@just.installer(check="brew --version")
def install_brew():
    """
    Install Homebrew package manager on macOS.
    """
    if just.system.platform != "darwin":
        raise NotImplementedError("Homebrew is only supported on macOS.")

    if just.system.pms.brew.is_available():
        just.echo.info("Homebrew is already installed.")
        return

    just.echo.info("Installing Homebrew...")
    just.download_with_resume(
        "https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh",
        output_file="install-brew.sh"
    )
    just.execute_commands("chmod +x install-brew.sh")
    just.execute_commands("./install-brew.sh")
    just.execute_commands("rm install-brew.sh")
    just.echo.success("Homebrew installed successfully.")
