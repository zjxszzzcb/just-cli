import just


@just.installer
def install_claude_code():
    """
    Install claude-code
    """
    if just.system.platform in ["linux", "darwin"]:
        just.download_with_resume('https://claude.ai/install.sh', output_file='install-claude-code.sh')
        just.execute_commands("bash install-claude-code.sh")
        just.execute_commands("just rm install-claude-code.sh")
    elif just.system.platform == "windows":
        if just.system.pms.winget.is_available():
            just.execute_commands("winget install Anthropic.ClaudeCode")
        else:
            just.download_with_resume('https://claude.ai/install.ps1', output_file='install-claude-code.ps1')
            just.execute_commands(r"iex .\install-claude-code.ps1")
            just.execute_commands("just rm install-claude-code.ps1")
    else:
        raise NotImplementedError(f"claude-code installer is not supported on {just.system.platform}.")
