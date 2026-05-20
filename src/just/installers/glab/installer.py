import just


@just.installer(check="glab version")
def install_glab():
    """Install GitLab CLI (glab)."""

    if just.system.platform == "darwin":
        if just.system.pms.brew.is_available():
            just.execute_commands("brew install glab")
        else:
            raise NotImplementedError(
                "Homebrew is required to install glab on macOS.\n"
                "Visit: https://gitlab.com/gitlab-org/cli/-/releases"
            )

    elif just.system.platform == "windows":
        if just.system.pms.winget.is_available():
            just.execute_commands("winget install glab.glab")
        else:
            raise NotImplementedError(
                "winget is required to install glab on Windows.\n"
                "Visit: https://gitlab.com/gitlab-org/cli/-/releases"
            )

    elif just.system.platform == "linux":
        _install_linux()

    else:
        raise NotImplementedError(
            f"glab is not supported on {just.system.platform}.\n"
            "Visit: https://gitlab.com/gitlab-org/cli/-/releases"
        )

    just.echo.success("GitLab CLI (glab) installed successfully.")


def _install_linux():
    arch_map = {"x86_64": "amd64", "aarch64": "arm64"}
    arch = arch_map.get(just.system.arch)
    if not arch:
        raise NotImplementedError(f"Unsupported arch: {just.system.arch}")

    if just.system.pms.brew.is_available():
        just.execute_commands("brew install glab")
        return

    if just.system.pms.apt.is_available():
        try:
            just.execute_commands(
                "sudo apt update && sudo apt install -y glab"
            )
            return
        except Exception:
            pass

    url = (
        "https://gitlab.com/gitlab-org/cli/-/releases/permalink/latest/"
        f"downloads/glab_linux_{arch}.tar.gz"
    )
    just.ArchiveInstaller(
        url=url,
        executables=["glab"],
        name="glab",
    ).run()
