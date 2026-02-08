import just
import os
import tempfile
import shutil
from pathlib import Path

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
    else:
        # Download and install binary from GitHub releases
        # Map platform and arch to OpenCode's naming convention
        platform_map = {
            "linux": "linux",
            "darwin": "darwin",
            "windows": "windows"
        }
        arch_map = {
            "x86_64": "x64",
            "aarch64": "arm64"
        }

        platform = platform_map[just.system.platform]
        arch = arch_map[just.system.arch]

        # Determine file extension
        if just.system.platform == "linux":
            ext = ".tar.gz"
        else:
            ext = ".zip"

        # Build download URL
        filename = f"opencode-{platform}-{arch}{ext}"
        url = f"https://github.com/anomalyco/opencode/releases/latest/download/{filename}"

        # Setup installation paths
        home = Path.home()
        cache_dir = home / ".cache" / "just"
        installed_dir = cache_dir / "installed"
        bin_dir = home / ".just" / "bin"

        # Create directories
        installed_dir.mkdir(parents=True, exist_ok=True)
        bin_dir.mkdir(parents=True, exist_ok=True)

        # Download archive
        with tempfile.TemporaryDirectory() as tmp_dir:
            archive_path = os.path.join(tmp_dir, filename)
            just.download_with_resume(url, output_file=archive_path)

            # Extract archive
            extract_dir = os.path.join(tmp_dir, "extracted")
            os.makedirs(extract_dir, exist_ok=True)

            if just.system.platform == "linux":
                just.extract(archive_path, extract_dir)
            else:
                just.extract(archive_path, extract_dir)

            # Find and copy opencode binary
            binary_source = os.path.join(extract_dir, "opencode")
            if not os.path.exists(binary_source):
                raise FileNotFoundError(f"opencode binary not found in {extract_dir}")

            binary_dest = installed_dir / "opencode"
            shutil.copy2(binary_source, binary_dest)
            os.chmod(binary_dest, 0o755)

            # Create symlink in ~/.just/bin/
            link_path = bin_dir / "opencode"
            if link_path.exists() or link_path.is_symlink():
                link_path.unlink()

            os.symlink(binary_dest, link_path)
            just.echo.success(f"OpenCode installed successfully to {link_path}")

            # Check PATH
            path_env = os.environ.get("PATH", "")
            if str(bin_dir) not in path_env.split(os.pathsep):
                just.echo.warning(f"{bin_dir} is not in your PATH")
