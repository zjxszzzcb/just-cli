import just


@just.installer
def install_docker():
    """
    Install Docker
    """
    if just.system.platform == "linux":
        just.download_with_resume("https://get.docker.com", output_file='install-docker.sh')
        just.execute_commands("sudo sh install-docker.sh --dry-run")
        if just.confirm_action("Confirm installation"):
            just.execute_commands("sudo sh install-docker.sh")
        just.execute_commands("just rm install-docker.sh")
    else:
        raise NotImplementedError(f"Docker installer is not supported on {just.system.platform}.")
