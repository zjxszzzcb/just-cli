import just


@just.installer
def install_qodercli():
    """
    Install qodercli
    """
    if just.system.platform == "linux":
        just.download_with_resume('https://qoder.com/install', output_file='install-qodercli.sh')
        just.execute_commands("bash install-qodercli.sh")
        just.execute_commands("just rm install-qodercli.sh")
    else:
        raise NotImplementedError(f"qodercli installer is not supported on {just.system.platform}.")
