"""Script-based installers (bash, powershell)."""

import os
import subprocess
import tempfile
from abc import ABC, abstractmethod
from typing import List, Optional, Union

import httpx

from just.utils import echo


class RemoteScriptInstaller(ABC):
    """
    Abstract base class for remote script-based installers.

    Provides common functionality for executing commands in different shells.
    """

    shell_type: str = "unknown"

    def __init__(
        self,
        commands: Optional[Union[str, List[str]]] = None,
        script_url: Optional[str] = None,
        name: Optional[str] = None,
        cache_enabled: bool = True,
        keep_cache: bool = False,
    ):
        """
        Initialize RemoteScriptInstaller.

        Args:
            commands: Shell command(s) to execute directly
            script_url: URL to download and execute script from
            name: Script name for caching (e.g., "opencode" → "install_opencode.sh")
            cache_enabled: Use cache directory instead of temp file
            keep_cache: Keep script after execution (for debugging)

        Raises:
            ValueError: If both or neither of commands and script_url are provided
        """
        if (commands is None) == (script_url is None):
            raise ValueError(
                f"Either 'commands' or 'script_url' must be provided, "
                f"but not both for {self.shell_type} installer"
            )

        self.commands = commands
        self.script_url = script_url
        self.name = name
        self.cache_enabled = cache_enabled
        self.keep_cache = keep_cache
        self._temp_file: Optional[str] = None

    def _get_cache_dir(self):
        """Get cache directory for installer scripts."""
        from pathlib import Path

        cache_dir = Path.home() / ".just" / "cache" / "installer" / "scripts"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir

    def _get_script_filename(self) -> str:
        """Generate filename for cached script."""
        if self.name:
            return f"install_{self.name}.sh"

        # Use URL hash for unnamed scripts
        import hashlib
        try:
            url_hash = hashlib.sha256(self.script_url.encode()).hexdigest()[:12]
            return f"install_{url_hash}.sh"
        except Exception:
            # Fallback to timestamp
            import time
            return f"install_{int(time.time())}.sh"

    @classmethod
    @abstractmethod
    def from_url(cls, url: str) -> "ScriptInstaller":
        """
        Create an installer instance from a script URL.

        Args:
            url: URL to download script from

        Returns:
            ScriptInstaller instance with the downloaded script content

        Raises:
            RuntimeError: If download fails
        """
        raise NotImplementedError

    def run(self) -> None:
        """
        Execute the script with streaming output.

        Raises:
            RuntimeError: If download or execution fails
        """
        try:
            if self.script_url is not None:
                self._download_script()
                self._execute_script()
            else:
                self._execute_commands()
        finally:
            self._cleanup()

    def _download_script(self) -> None:
        """Download script from URL to cache or temp file."""
        if self.script_url is None:
            return

        echo.info(f"Downloading {self.shell_type} script from {self.script_url}")

        # Determine file location based on cache_enabled
        if self.cache_enabled:
            cache_dir = self._get_cache_dir()
            filename = self._get_script_filename()
            script_path = cache_dir / filename

            # Check if already cached
            if script_path.exists():
                echo.info(f"Using cached script: {script_path}")
                self._temp_file = str(script_path)
                return

            # Download to cache
            try:
                from just.utils.download_utils import download_with_resume

                success = download_with_resume(
                    url=self.script_url,
                    output_file=str(script_path),
                    verbose=False
                )

                if not success:
                    raise RuntimeError(f"Failed to download script from {self.script_url}")

                self._temp_file = str(script_path)
                echo.info(f"Script cached to: {script_path}")
            except Exception as e:
                raise RuntimeError(f"Failed to download script: {e}")
        else:
            # Use temp file (backward compatible)
            temp_fd, self._temp_file = tempfile.mkstemp(suffix=f".{self.shell_type}")
            os.close(temp_fd)

            try:
                from just.utils.download_utils import download_with_resume

                success = download_with_resume(
                    url=self.script_url,
                    output_file=self._temp_file,
                    verbose=False
                )

                if not success:
                    raise RuntimeError(f"Failed to download script from {self.script_url}")

                echo.info(f"Script downloaded to temp file: {self._temp_file}")
            except Exception as e:
                raise RuntimeError(f"Failed to download script: {e}")

    def _execute_script(self) -> None:
        """Execute the downloaded script."""
        if self._temp_file is None:
            raise RuntimeError("No script file to execute")

        if self.shell_type == "bash":
            cmd = f"bash {self._temp_file}"
        elif self.shell_type == "powershell":
            cmd = f"powershell -ExecutionPolicy Bypass -File {self._temp_file}"
        else:
            raise RuntimeError(f"Unsupported shell type: {self.shell_type}")

        self._run_command(cmd)

    def _execute_commands(self) -> None:
        """Execute inline commands."""
        if self.commands is None:
            return

        # Convert to list if string
        if isinstance(self.commands, str):
            commands_list = [self.commands]
        else:
            commands_list = self.commands

        # Join commands based on shell type
        if self.shell_type == "bash":
            cmd = " && ".join(commands_list)
        elif self.shell_type == "powershell":
            cmd = " | ".join(commands_list)
        else:
            raise RuntimeError(f"Unsupported shell type: {self.shell_type}")

        self._run_command(cmd)

    def _run_command(self, cmd: str) -> None:
        """Run command with streaming output."""
        echo.info(f"Executing: {cmd}")

        process = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        if process.stdout:
            for line in process.stdout:
                echo.info(line.rstrip())

        if process.stderr:
            for line in process.stderr:
                echo.error(line.rstrip())

        process.wait()

        if process.returncode != 0:
            raise RuntimeError(
                f"Command execution failed with exit code {process.returncode}"
            )

        echo.success("Execution completed successfully")

    def _cleanup(self) -> None:
        """Clean up temporary files or retain based on keep_cache setting."""
        if self._temp_file is None or not os.path.exists(self._temp_file):
            return

        # Skip cleanup if user wants to keep cache
        if self.cache_enabled and self.keep_cache:
            echo.info(f"Script retained at: {self._temp_file}")
            return

        # Always cleanup temp files or cache when keep_cache=False
        try:
            os.remove(self._temp_file)
            echo.debug(f"Cleaned up: {self._temp_file}")
        except Exception as e:
            echo.warning(f"Failed to cleanup {self._temp_file}: {e}")


class BashScriptInstaller(RemoteScriptInstaller):
    """
    Installer for bash scripts.

    Executes bash commands directly or downloads and runs a script from URL.
    """

    shell_type = "bash"

    @classmethod
    def from_url(cls, url: str) -> "BashScriptInstaller":
        """
        Create a BashScriptInstaller from a script URL.

        Args:
            url: URL to download bash script from

        Returns:
            BashScriptInstaller instance with the downloaded script content
        """
        return cls(script_url=url)


class PowerShellInstaller(RemoteScriptInstaller):
    """
    Installer for PowerShell scripts.

    Executes PowerShell commands directly or downloads and runs a script from URL.
    """

    shell_type = "powershell"

    @classmethod
    def from_url(cls, url: str) -> "PowerShellInstaller":
        """
        Create a PowerShellInstaller from a script URL.

        Args:
            url: URL to download PowerShell script from

        Returns:
            PowerShellInstaller instance with the downloaded script content
        """
        return cls(script_url=url)
