"""Installers for binary releases and archives."""

import os
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse

from just.core.config.utils import get_bin_dir, get_cache_dir, get_releases_dir
from just.utils import echo
from just.utils.archive import extract
from just.utils.download_utils import download_with_resume
from just.utils.file_utils import mkdir, search_file
from just.core.installer.utils import (
    create_symlink_or_wrapper,
    make_executable,
    check_path_included,
)


class BinaryInstaller:
    """
    Installer for single-binary releases.

    Downloads binary, makes it executable, and creates symlink in bin/.

    Directory structure:
        ~/.just/bin/<alias>              # Direct binary placement
    """

    def __init__(self, url: str, alias: str, headers: Optional[Dict[str, str]] = None):
        """
        Initialize BinaryInstaller.

        Args:
            url: Download URL for the binary
            alias: Name of the binary (used for installation)
            headers: Optional HTTP headers for download
        """
        self.url = url
        self.alias = alias
        self.headers = headers or {}

    def run(self) -> None:
        """
        Execute installation: download, chmod +x.
        """
        # 1. Download directly to bin/
        self._download()

        # 2. Make executable
        binary_path = get_bin_dir() / self.alias
        make_executable(binary_path)

        # 3. Check PATH
        check_path_included(get_bin_dir())

        echo.success(f"Installation of {self.alias} completed successfully!")

    def _download(self) -> None:
        """Download binary directly to bin directory."""
        echo.info(f"Downloading from {self.url}")

        # Ensure bin directory exists
        bin_dir = get_bin_dir()
        mkdir(str(bin_dir))

        # Target path in bin/
        binary_path = bin_dir / self.alias

        # Check if already exists
        if binary_path.exists():
            echo.info(f"Binary already exists: {binary_path}, re-downloading...")

        download_with_resume(
            url=self.url,
            headers=self.headers,
            output_file=str(binary_path),
            verbose=False,
        )


class ArchiveInstaller:
    """
    Installer for pre-compiled release archives.

    Downloads archive, extracts it, and creates symlinks to executables.

    Directory structure:
        ~/.just/cache/                    # Downloaded archives (auto-cleanup)
        ~/.just/releases/<tool>/           # Extracted files
        ~/.just/bin/<tool> -> ../releases/<tool>/bin/tool  # Symlinks
    """

    def __init__(
        self,
        url: str,
        executables: Optional[List[str]] = None,
        headers: Optional[Dict[str, str]] = None,
        name: Optional[str] = None,
    ):
        """
        Initialize ArchiveInstaller.

        Args:
            url: Download URL for the release archive
            executables: Executable file names/paths to symlink (auto-detect if None)
            headers: Optional HTTP headers for download
            name: Custom release directory name (auto-generated from filename if None)
        """
        self.url = url
        self.executables = executables
        self.headers = headers or {}

        # Extract filename from URL
        parsed_url = urlparse(url)
        self.archive_filename = os.path.basename(parsed_url.path)
        if not self.archive_filename:
            raise ValueError(f"Cannot extract filename from URL: {url}")

        # Determine extraction directory name
        if name:
            # Use custom name if provided
            self.extract_dirname = name
        else:
            # Auto-generate from filename
            self.extract_dirname = self._get_extract_dirname(self.archive_filename)

    def run(self) -> None:
        """
        Execute installation: download, extract, symlink.

        Raises:
            Exception: If any step fails
        """
        # 1. Download
        cache_file = self._download()

        # 2. Extract
        extract_dir = self._extract(cache_file)

        # 3. Find executables
        executables = self._find_executables(extract_dir)
        if not executables:
            raise Exception("No executables found in archive")

        # 4. Create symlinks
        self._create_symlinks(executables)

        # 5. Clean up cache
        self._cleanup_cache(cache_file)

        # 6. Check PATH and warn if needed
        check_path_included(get_bin_dir())

        echo.success(f"Installation completed successfully!")

    def _download(self) -> Path:
        """Download archive to cache directory."""
        echo.info(f"Downloading from {self.url}")

        # Ensure cache directory exists
        cache_dir = get_cache_dir()
        mkdir(str(cache_dir))

        # Download file
        cache_file = cache_dir / self.archive_filename

        download_with_resume(
            url=self.url,
            headers=self.headers,
            output_file=str(cache_file),
            verbose=False,
        )

        return cache_file

    def _extract(self, cache_file: Path) -> Path:
        """Extract archive to releases directory."""
        extract_dir = get_releases_dir() / self.extract_dirname

        # Check if already extracted
        if extract_dir.exists():
            echo.info(f"Already extracted: {extract_dir}")
            return extract_dir

        echo.info(f"Extracting {self.archive_filename}")

        # Ensure releases directory exists
        releases_dir = get_releases_dir()
        mkdir(str(releases_dir))

        # Extract archive
        if not extract(str(cache_file), str(extract_dir)):
            raise Exception("Extraction failed")

        return extract_dir

    def _find_executables(self, extract_dir: Path) -> List[str]:
        """Find executable files in extracted directory."""
        if self.executables:
            # User specified executables
            found_executables = []
            for exe in self.executables:
                exe_path = search_file(str(extract_dir), exe)
                if exe_path:
                    found_executables.append(exe_path)
                else:
                    echo.warning(f"Executable not found: {exe}")

            return found_executables
        else:
            # Auto-detect executables
            return self._auto_detect_executables(extract_dir)

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

    def _find_executables_in_dir(
        self, directory: Path, recursive: bool = False
    ) -> List[str]:
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
        if os.name == "nt":
            return file_path.suffix.lower() in [".exe", ".bat", ".cmd", ".ps1"]

        # Unix: check for executable permission
        import stat
        file_stat = file_path.stat()
        return bool(file_stat.st_mode & stat.S_IXUSR)

    def _create_symlinks(self, executables: List[str]):
        """Create symlinks/wrapper scripts in ~/.just/bin/ for executables."""
        echo.info(f"Creating symlinks in {get_bin_dir()}")

        for exe_path in executables:
            exe_name = Path(exe_path).name
            target_path = Path(exe_path)

            create_symlink_or_wrapper(
                target=target_path,
                link_dir=get_bin_dir(),
                link_name=exe_name
            )

    def _cleanup_cache(self, cache_file: Path) -> None:
        """Clean up downloaded archive file."""
        try:
            if cache_file.exists():
                cache_file.unlink()
                echo.debug(f"Cleaned up cache file: {cache_file}")
        except Exception as e:
            echo.warning(f"Failed to clean up cache file {cache_file}: {e}")

    @staticmethod
    def _get_extract_dirname(filename: str) -> str:
        """
        Get extraction directory name by removing archive extensions.

        Examples:
            ripgrep-14.1.0-x86_64.tar.gz -> ripgrep-14.1.0-x86_64
            tool-1.0.0.zip -> tool-1.0.0
            archive.tar.bz2 -> archive
        """
        return filename.split(".", 1)[0]
