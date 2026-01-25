import just


@just.installer
def install_nvm(
    version: just.Annotated[str, just.Option(
        '-v', '--version',
        help="The version of nvm to install."
    )] = ""
):
    """
    Install TUI SSH Manager
    """
    just.execute_commands("pip install https://github.com/zjxszzzcb/ssh-manager/releases/download/v0.1.0/ssh_manager-0.1.0-py3-none-any.whl")
