import just


@just.installer(check="edit -v")
def install_edit(
    version: just.Annotated[
        str, just.Option("-v", "--version", help="The version of Edit to install.")
    ] = "1.2.0",
):
    """
    Install Microsoft Edit.
    """

    if just.system.platform == "windows":
        url = f"https://github.com/microsoft/edit/releases/download/v{version}/edit-{version}-{just.system.arch}-windows.zip"
        just.ArchiveInstaller(
            url=url,
            executables=["edit.exe"],
            name="edit",
        ).run()
    elif just.system.platform == "linux":
        url = f"https://github.com/microsoft/edit/releases/download/v{version}/edit-{version}-{just.system.arch}-linux-gnu.tar.zst"
        just.ArchiveInstaller(
            url,
            executables=["edit"],
            name="edit",
        ).run()
    else:
        raise NotImplementedError(
            f"Microsoft Edit is not supported on {just.system.platform}."
        )
