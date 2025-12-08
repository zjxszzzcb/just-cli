import just


@just.installer
def install_nvm(
    version: just.Annotated[str, just.Option(
        '-v', '--version',
        help="The version of nvm to install."
    )] = ""
):
    """
    Install Microsoft Edit.
    """
    if just.system.platform == "windows":
        if not version:
            version = "1.2.2"
        just.execute_commands([
            f"just download https://github.com/coreybutler/nvm-windows/releases/download/{version}/nvm-setup.exe",
            "./nvm-setup.exe"
            "just rm ./nvm-setup.exe"
        ])
    elif just.system.platform == "linux":
        if not version:
            version = "0.39.5"
        just.execute_commands([
            f"just download https://raw.githubusercontent.com/nvm-sh/nvm/v{version}/install.sh -o install_nvm.sh",
            "bash install_nvm.sh",
            "rm install_nvm.sh"
        ])
    else:
        raise NotImplementedError(f"Microsoft Edit is not supported on {just.system.platform}.")
