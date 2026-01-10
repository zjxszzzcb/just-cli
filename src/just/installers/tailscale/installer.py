import just


@just.installer
def install_tailscale():
    """
    Install tailscale curl -fsSL  | sh
    """
    if just.system.platform == "linux":
        just.download_with_resume('https://tailscale.com/install.sh', output_file='install-tailscale.sh')
        just.execute_commands("sh install-tailscale.sh")
        just.execute_commands("just rm install-tailscale.sh")
        just.execute_commands("sudo tailscale up")
    else:
        raise NotImplementedError(f"tailscale installer is not supported on {just.system.platform}.")
