import os
import stat
from pathlib import Path
from typing import Dict, Optional

import just.utils.echo_utils as echo
from just.utils.download_utils import download_with_resume
from just.utils.file_utils import mkdir, symlink


class BinaryInstaller:
    """
    Installer for single-binary releases.
    
    Downloads binary, makes it executable, and creates symlink.
    
    Directory structure:
        ~/.cache/just/installed/<alias>  # The binary itself
        ~/.just/bin/<alias>              # Symlink
    """
    
    def __init__(
        self,
        url: str,
        alias: str,
        headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize BinaryInstaller.
        
        Args:
            url: Download URL for the binary
            alias: Name of the binary (used for installation and symlink)
            headers: Optional HTTP headers for download
        """
        self.url = url
        self.alias = alias
        self.headers = headers or {}
        
        # Setup directory paths
        home = Path.home()
        self.cache_dir = home / ".cache" / "just"
        self.installed_dir = self.cache_dir / "installed"
        self.bin_dir = home / ".just" / "bin"
        
    def run(self) -> None:
        """
        Execute installation: download, chmod +x, symlink.
        """
        # 1. Download
        self._download()

        # 2. Make executable
        self._make_executable()

        # 3. Create symlink
        self._create_symlink()

        # 4. Check PATH
        self._check_path()

        echo.success(f"Installation of {self.alias} completed successfully!")
    
    def _download(self) -> None:
        """Download binary to installed directory."""
        echo.info(f"Downloading from {self.url}")
        
        # Create installed directory
        mkdir(str(self.installed_dir))
        
        # Target path
        binary_path = self.installed_dir / self.alias
        
        # Check if already exists (simple check, could be improved with versioning)
        if binary_path.exists():
            echo.info(f"Binary already exists: {binary_path}")
            # We continue to ensure symlinks are correct even if file exists
        
        download_with_resume(
            url=self.url,
            headers=self.headers,
            output_file=str(binary_path),
            verbose=False
        )
    
    def _make_executable(self) -> None:
        """Make the downloaded file executable."""
        binary_path = self.installed_dir / self.alias
        
        if os.name != 'nt':
            st = os.stat(binary_path)
            os.chmod(binary_path, st.st_mode | stat.S_IEXEC)
            echo.info(f"Made executable: {binary_path}")

    def _create_symlink(self):
        """Create symlink/wrapper in ~/.just/bin/."""
        echo.info(f"Creating symlink in {self.bin_dir}")
        
        # Create bin directory
        mkdir(str(self.bin_dir))
        
        binary_path = self.installed_dir / self.alias
        
        if os.name == 'nt':
            # Windows: Create wrapper batch script
            self._create_windows_wrapper(str(binary_path), self.alias)
        else:
            # Unix: Create symlink
            self._create_unix_symlink(str(binary_path), self.alias)
    
    def _create_unix_symlink(self, target_path: str, link_name: str):
        """Create symlink on Unix systems."""
        link_path = self.bin_dir / link_name
        
        # Remove existing symlink if it exists
        if link_path.exists() or link_path.is_symlink():
            link_path.unlink()
        
        # Create symlink
        symlink(target_path, str(link_path))
        echo.info(f"Created symlink: {link_name} -> {target_path}")
    
    def _create_windows_wrapper(self, target_path: str, wrapper_name: str):
        """Create wrapper batch script on Windows."""
        wrapper_path = self.bin_dir / f"{wrapper_name}.bat"
        
        # Remove existing wrapper if it exists
        if wrapper_path.exists():
            wrapper_path.unlink()
        
        # Create batch wrapper script
        try:
            wrapper_content = f'@echo off\r\n"{target_path}" %*\r\n'
            with open(wrapper_path, 'w') as f:
                f.write(wrapper_content)
            echo.info(f"Created wrapper script: {wrapper_name}.bat -> {target_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to create wrapper for {wrapper_name}: {e}")

    def _check_path(self):
        """Check if ~/.just/bin is in PATH and warn if not."""
        # Reuse logic from SimpleReleaseInstaller or extract to common utility
        # For now, simple implementation
        path_env = os.environ.get("PATH", "")
        bin_dir_str = str(self.bin_dir.resolve())
        
        if bin_dir_str not in path_env.split(os.pathsep):
            echo.warning(f"{self.bin_dir} is not in your PATH")
