import just

from just.core.installer.utils import create_symlink_or_wrapper
from just.core.config.utils import get_bin_dir


@just.installer(check="edit -v")
def install_edit(
    version: just.Annotated[
        str, just.Option("-v", "--version", help="The version of Edit to install.")
    ] = None,
):
    """
    Install a terminal text editor.

    - Windows/Linux: Microsoft Edit
    - macOS: micro (with 'edit' symlink)
    """
    # Resolve default version based on platform
    if version is None:
        if just.system.platform == "darwin":
            version = "2.0.15"  # micro latest stable
        else:
            version = "1.2.0"  # Microsoft Edit

    if just.system.platform == "windows":
        just.echo.info(f"Installing Microsoft Edit v{version} as the default editor...")
        url = f"https://github.com/microsoft/edit/releases/download/v{version}/edit-{version}-{just.system.arch}-windows.zip"
        just.ArchiveInstaller(
            url=url,
            executables=["edit.exe"],
            name="edit",
        ).run()
    elif just.system.platform == "linux":
        just.echo.info(f"Installing Microsoft Edit v{version} as the default editor...")
        url = f"https://github.com/microsoft/edit/releases/download/v{version}/edit-{version}-{just.system.arch}-linux-gnu.tar.zst"
        just.ArchiveInstaller(
            url,
            executables=["edit"],
            name="edit",
        ).run()
    elif just.system.platform == "darwin":
        # Install micro text editor for macOS
        editor_name = "micro"
        # Map architecture to micro's platform naming
        micro_platform = "macos-arm64" if just.system.arch == "aarch64" else "osx"
        url = f"https://github.com/micro-editor/micro/releases/download/v{version}/micro-{version}-{micro_platform}.tar.gz"

        just.echo.info(f"Installing {editor_name} v{version} as the default editor...")

        just.ArchiveInstaller(
            url=url,
            executables=["micro"],
            name="micro",
        ).run()

        # Create edit -> micro symlink for consistency
        micro_path = get_bin_dir() / "micro"

        # Verify micro was installed successfully before creating symlink
        if not micro_path.exists():
            raise RuntimeError(f"micro installation failed - executable not found at {micro_path}")

        create_symlink_or_wrapper(
            target=micro_path,
            link_dir=get_bin_dir(),
            link_name="edit"
        )
    else:
        raise NotImplementedError(
            f"No editor is available for {just.system.platform}."
        )
