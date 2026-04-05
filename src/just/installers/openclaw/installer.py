import just


@just.installer(check="openclaw --version")
def install_openclaw():
    """
    Install OpenClaw - An open-source personal AI assistant that runs on your computer.
    Integrates with WhatsApp, Telegram, Discord, and iMessage.
    """
    if just.system.platform == "windows":
        just.download_with_resume(
            'https://openclaw.ai/install.ps1',
            output_file='install-openclaw.ps1'
        )
        just.execute_commands("iex .\\install-openclaw.ps1")
        just.execute_commands("rm install-openclaw.ps1")
    else:
        just.download_with_resume(
            'https://openclaw.ai/install.sh',
            output_file='install-openclaw.sh'
        )
        just.execute_commands("bash install-openclaw.sh")
        just.execute_commands("rm install-openclaw.sh")

