import subprocess

import just


@just.installer(check="micro --version")
def install_micro():
    """Install micro, a modern terminal-based text editor."""

    if just.system.platform == "darwin":
        if just.system.pms.brew.is_available():
            just.execute_commands("brew install micro")
        else:
            _install_via_getmicroro()
            just.echo.success("micro installed successfully.")
        return

    if just.system.platform == "linux":
        _install_via_getmicroro()
        just.echo.success("micro installed successfully.")
        return

    if just.system.platform == "windows":
        if just.system.pms.winget.is_available():
            just.execute_commands("winget install --id Micro.Micro")
        else:
            raise NotImplementedError(
                "winget is required to install micro on Windows.\n"
                "Visit: https://micro-editor.github.io/"
            )
        return

    raise NotImplementedError(f"micro is not supported on {just.system.platform}")


def _install_via_getmicroro():
    """Install micro via the official getmic.ro installer.

    getmic.ro places the binary in the current working directory. We cd into
    a directory on PATH so micro is usable immediately. Linux and macOS use
    /usr/local/bin (with sudo when not writable); falls back to ~/.local/bin.

    A plain `curl ... | bash` needs a shell to interpret the pipe, so we run
    it through subprocess with shell=True rather than just.execute_commands
    (which shlex-splits and would pass '|' to curl as a literal argument).
    """
    import os

    # Pick an install dir that is on PATH and writable.
    candidates = ["/usr/local/bin", os.path.expanduser("~/.local/bin")]
    target = next((d for d in candidates if os.access(d, os.W_OK)), None)

    if target is None:
        # /usr/local/bin exists but needs sudo; create ~/.local/bin as fallback.
        target = os.path.expanduser("~/.local/bin")
        os.makedirs(target, exist_ok=True)
        cmd = f"cd {target}; curl -fsSL https://getmic.ro | sudo bash"
    elif target == "/usr/local/bin":
        cmd = f"cd {target}; curl -fsSL https://getmic.ro | bash"
    else:
        cmd = f"cd {target}; curl -fsSL https://getmic.ro | bash"

    just.echo.info(f"Installing micro to {target} ...")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"getmic.ro installer exited with code {result.returncode}.\n"
            "Visit: https://micro-editor.github.io/ for manual installation."
        )
