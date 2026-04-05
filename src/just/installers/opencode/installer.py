import just


@just.installer(check="opencode --version")
def install_opencode():
    """
    Install OpenCode - An open-source AI coding agent for the terminal.
    Supports multiple LLM providers including Claude, GPT, Gemini, and more.
    Integrates with VS Code, Cursor, and other IDEs.
    """
    # Try package managers first
    if just.system.pms.brew.is_available():
        just.execute_commands("brew install anomalyco/tap/opencode")
    elif just.system.tools.npm.is_available():
        just.execute_commands("npm install -g opencode-ai")
    elif just.system.platform in ('linux', 'darwin'):
        just.BashScriptInstaller(
            script_url="https://opencode.ai/install",
            name="opencode"
        ).run()
