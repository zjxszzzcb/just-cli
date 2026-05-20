import just


@just.installer
def install_mssh():
    """
    Install TUI SSH Manager
    """
    just.execute_commands("pip install git+https://github.com/zjxszzzcb/ssh-manager.git")
