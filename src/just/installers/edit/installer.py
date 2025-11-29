import just


@just.installer
def install_edit(
    version: just.Annotated[str, just.Option(
        '-v', '--version',
        help="The version of Edit to install."
    )] = "1.2.0"
):
    """
    Install Microsoft Edit.
    """
    if just.system.platform == "windows":
        just.SimpleReleaseInstaller(
            url = f"https://github.com/microsoft/edit/releases/download/v{version}/edit-{version}-{just.system.arch}-windows.zip",
            executables=["edit.exe"]
        ).run()
    elif just.system.platform == "linux":
        url = f"https://github.com/microsoft/edit/releases/download/v{version}/edit-{version}-{just.system.arch}-linux-gnu.tar.zst"
        just.SimpleReleaseInstaller(url, executables=["edit"]).run()
    else:
        raise NotImplementedError(f"Microsoft Edit is not supported on {just.system.platform}.")
