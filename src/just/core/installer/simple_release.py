import os
import stat
from pathlib import Path
from typing import List, Optional, Dict
from urllib.parse import urlparse

import just.utils.echo_utils as echo
from just.utils.download_utils import download_with_resume
from just.utils.archive import extract
from just.utils.file_utils import mkdir, symlink, search_file


class SimpleReleaseInstaller:
    """
    Simple installer for pre-compiled release archives.
    
    Downloads archive, extracts it, and creates symlinks to executables.
    
    Directory structure:
        ~/.cache/just/downloads/        # Downloaded archives
        ~/.cache/just/installed/        # Extracted files
        ~/.just/bin/                    # Symlinks to executables
    
    Note: Add ~/.just/bin to your PATH if not already done.
    """
    
    def __init__(
        self,
        url: str,
        executables: Optional[List[str]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize SimpleReleaseInstaller.
        
        Args:
            url: Download URL for the release archive
            executables: Executable file names/paths to symlink (auto-detect if None)
            headers: Optional HTTP headers for download
        """
        self.url = url
        self.executables = executables
        self.headers = headers or {}
        
        # Setup directory paths
        home = Path.home()
        self.cache_dir = home / ".cache" / "just"
        self.downloads_dir = self.cache_dir / "downloads"
        self.installed_dir = self.cache_dir / "installed"
        self.bin_dir = home / ".just" / "bin"
        
        # Extract filename from URL
        parsed_url = urlparse(url)
        self.archive_filename = os.path.basename(parsed_url.path)
        if not self.archive_filename:
            raise ValueError(f"Cannot extract filename from URL: {url}")
        
        # Determine extraction directory name (remove common archive extensions)
        self.extract_dirname = self._get_extract_dirname(self.archive_filename)
        
    def run(self) -> None:
        """
        Execute installation: download, extract, symlink.
        
        Raises:
            Exception: If any step fails
        """
        # 1. Download
        self._download()

        # 2. Extract
        self._extract()

        # 3. Find executables
        executables = self._find_executables()
        if not executables:
            raise Exception("No executables found in archive")

        # 4. Create symlinks
        self._create_symlinks(executables)

        # 5. Check PATH and warn if needed
        self._check_path()

        echo.success(f"Installation completed successfully!")
    
    def _download(self) -> None:
        """Download archive to downloads directory."""
        echo.info(f"Downloading from {self.url}")
        
        # Create downloads directory
        mkdir(str(self.downloads_dir))
        
        # Download file
        archive_path = self.downloads_dir / self.archive_filename
        
        # Check if already downloaded
        if archive_path.exists():
            echo.info(f"Archive already exists: {archive_path}")
            return
        
        download_with_resume(
            url=self.url,
            headers=self.headers,
            output_file=str(archive_path),
            verbose=False
        )
    
    def _extract(self):
        """Extract archive to installed directory."""
        archive_path = self.downloads_dir / self.archive_filename
        extract_path = self.installed_dir / self.extract_dirname
        
        # Check if already extracted
        if extract_path.exists():
            echo.info(f"Already extracted: {extract_path}")
            return
        
        echo.info(f"Extracting {self.archive_filename}")
        
        # Create installed directory
        mkdir(str(self.installed_dir))
        
        # Extract archive
        if not extract(str(archive_path), str(extract_path)):
            raise Exception("Extraction failed")
    
    def _find_executables(self) -> List[str]:
        """Find executable files in extracted directory."""
        extract_path = self.installed_dir / self.extract_dirname
        
        if self.executables:
            # User specified executables
            found_executables = []
            for exe in self.executables:
                exe_path = search_file(str(extract_path), exe)
                if exe_path:
                    found_executables.append(exe_path)
                else:
                    echo.warning(f"Executable not found: {exe}")
            
            return found_executables
        else:
            # Auto-detect executables
            return self._auto_detect_executables(extract_path)
    
    def _auto_detect_executables(self, root_dir: Path) -> List[str]:
        """
        Auto-detect executable files in directory.
        
        Searches for files that:
        - Are in bin/ or root directory
        - Have executable permission (Unix) or .exe extension (Windows)
        - Are actual files (not directories)
        """
        executables = []
        
        # Check bin/ directory first
        bin_path = root_dir / "bin"
        if bin_path.exists() and bin_path.is_dir():
            executables.extend(self._find_executables_in_dir(bin_path))
        
        # If no executables found in bin/, check root
        if not executables:
            executables.extend(self._find_executables_in_dir(root_dir, recursive=False))
        
        return executables
    
    def _find_executables_in_dir(self, directory: Path, recursive: bool = False) -> List[str]:
        """Find executable files in a specific directory."""
        executables = []
        
        if not directory.exists():
            return executables
        
        # Get all files in directory
        if recursive:
            files = directory.rglob("*")
        else:
            files = directory.glob("*")
        
        for file_path in files:
            if not file_path.is_file():
                continue
            
            # Check if file is executable
            if self._is_executable(file_path):
                executables.append(str(file_path.resolve()))
        
        return executables

    @staticmethod
    def _is_executable(file_path: Path) -> bool:
        """Check if file is executable."""
        # Windows: check for .exe, .bat, .cmd extensions
        if os.name == 'nt':
            return file_path.suffix.lower() in ['.exe', '.bat', '.cmd', '.ps1']
        
        # Unix: check for executable permission
        file_stat = file_path.stat()
        return bool(file_stat.st_mode & stat.S_IXUSR)
    
    def _create_symlinks(self, executables: List[str]):
        """Create symlinks/wrapper scripts in ~/.just/bin/ for executables."""
        echo.info(f"Creating symlinks in {self.bin_dir}")
        
        # Create bin directory
        mkdir(str(self.bin_dir))
        
        for exe_path in executables:
            exe_name = Path(exe_path).name
            
            if os.name == 'nt':
                # Windows: Create wrapper batch script instead of symlink
                self._create_windows_wrapper(exe_path, exe_name)
            else:
                # Unix: Create symlink
                self._create_unix_symlink(exe_path, exe_name)
    
    def _create_unix_symlink(self, exe_path: str, exe_name: str):
        """Create symlink on Unix systems."""
        link_path = self.bin_dir / exe_name
        
        # Remove existing symlink if it exists
        if link_path.exists() or link_path.is_symlink():
            echo.info(f"Removing existing symlink: {link_path}")
            link_path.unlink()
        
        # Create symlink
        symlink(exe_path, str(link_path))
        echo.info(f"Created symlink: {exe_name} -> {exe_path}")
    
    def _create_windows_wrapper(self, exe_path: str, exe_name: str):
        """Create wrapper batch script on Windows."""
        # Remove .exe extension if present for wrapper name
        wrapper_name = exe_name.replace('.exe', '')
        wrapper_path = self.bin_dir / f"{wrapper_name}.bat"
        
        # Remove existing wrapper if it exists
        if wrapper_path.exists():
            echo.info(f"Removing existing wrapper: {wrapper_path}")
            wrapper_path.unlink()
        
        # Create batch wrapper script
        try:
            # Use absolute path and forward all arguments
            wrapper_content = f'@echo off\r\n"{exe_path}" %*\r\n'
            
            with open(wrapper_path, 'w') as f:
                f.write(wrapper_content)
            
            echo.info(f"Created wrapper script: {wrapper_name}.bat -> {exe_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to create wrapper for {exe_name}: {e}")
    
    def _check_path(self):
        """Check if ~/.just/bin is in PATH and warn if not."""
        path_env = os.environ.get("PATH", "")
        bin_dir_str = str(self.bin_dir.resolve())
        
        # Check if bin directory is in PATH
        if bin_dir_str not in path_env.split(os.pathsep):
            echo.warning("")
            echo.warning(f"{self.bin_dir} is not in your PATH")
            echo.info("Add the following to your shell config:")
            echo.info("")
            
            # Detect shell and provide instructions
            shell = os.environ.get("SHELL", "")
            
            if "bash" in shell:
                echo.info(f'  echo \'export PATH="$HOME/.just/bin:$PATH"\' >> ~/.bashrc')
                echo.info(f'  source ~/.bashrc')
            elif "zsh" in shell:
                echo.info(f'  echo \'export PATH="$HOME/.just/bin:$PATH"\' >> ~/.zshrc')
                echo.info(f'  source ~/.zshrc')
            elif "fish" in shell:
                echo.info(f'  fish_add_path ~/.just/bin')
            elif os.name == 'nt':
                echo.info(f'  setx PATH "%PATH%;%USERPROFILE%\\.just\\bin"')
            else:
                echo.info(f'  export PATH="$HOME/.just/bin:$PATH"')
            
            echo.info("")

    @staticmethod
    def _get_extract_dirname(filename: str) -> str:
        """
        Get extraction directory name by removing archive extensions.
        
        Examples:
            ripgrep-14.1.0-x86_64.tar.gz -> ripgrep-14.1.0-x86_64
            tool-1.0.0.zip -> tool-1.0.0
            archive.tar.bz2 -> archive
        """
        return filename.split('.', 1)[0]
