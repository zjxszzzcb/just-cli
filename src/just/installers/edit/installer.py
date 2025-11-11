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
    url = f"https://github.com/microsoft/edit/releases/download/v{version}/edit-{version}-{just.system.arch}-windows.zip"
    just.SimpleReleaseInstaller(url, executables=["edit.exe"]).run()
    just.update_env_config(just.config.keys.JUST_EDIT_USE_TOOL, 'edit.exe')
    # if just.system.pms.winget.is_available():
    #     just.execute_commands("winget install Microsoft.Edit")
    #     just.update_env_config(just.config.keys.JUST_EDIT_USE_TOOL, 'edit')
    # elif just.system.pms.snap.is_available():
    #     just.execute_commands("snap install msedit")
    #     just.update_env_config(just.config.keys.JUST_EDIT_USE_TOOL, 'msedit')
    # elif just.system.platform == "windows":
    #     url = f"https://github.com/microsoft/edit/releases/download/v{version}/edit-{version}-{just.system.arch}-windows.zip"
    #     just.SimpleReleaseInstaller(url, executables=["edit.exe"]).run()
    #     just.update_env_config(just.config.keys.JUST_EDIT_USE_TOOL, 'edit.exe')
    # elif just.system.platform == "linux":
    #     url = f"https://github.com/microsoft/edit/releases/download/v{version}/edit-{version}-{just.system.arch}-linux-gnu.tar.zst"
    #     just.SimpleReleaseInstaller(url, executables=["edit"]).run()
    #     just.update_env_config(just.config.keys.JUST_EDIT_USE_TOOL, 'edit')
