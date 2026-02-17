import os
import subprocess
import tempfile
from typing import List, Optional, Union

import just.utils.echo_utils as echo
from just.utils.download_utils import download_with_resume


class BashScriptInstaller:
    """
    Installer for bash scripts.
    
    Executes either inline commands or downloads and runs a script from URL.
    """

    def __init__(
        self,
        commands: Optional[Union[str, List[str]]] = None,
        script_url: Optional[str] = None
    ):
        """
        Initialize BashScriptInstaller.
        
        Args:
            commands: Bash command(s) to execute directly
            script_url: URL to download and execute the script from
            
        Raises:
            ValueError: If both or neither of commands and script_url are provided
        """
        # Validate mutual exclusivity
        if (commands is None) == (script_url is None):
            raise ValueError(
                "Either 'commands' or 'script_url' must be provided, but not both"
            )

        self.commands = commands
        self.script_url = script_url
        self._temp_file: Optional[str] = None

    def run(self) -> None:
        """
        Execute the bash script with streaming output.
        
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
        """Download script from URL to a temporary file."""
        if self.script_url is None:
            return

        echo.info(f"Downloading script from {self.script_url}")

        # Create temp file
        temp_fd, self._temp_file = tempfile.mkstemp(suffix='.sh')
        os.close(temp_fd)

        try:
            download_with_resume(
                url=self.script_url,
                output_file=self._temp_file,
                verbose=False
            )
            echo.info(f"Script downloaded to {self._temp_file}")
        except Exception as e:
            raise RuntimeError(f"Failed to download script: {e}")

    def _execute_script(self) -> None:
        """Execute the downloaded script."""
        if self._temp_file is None:
            raise RuntimeError("No script file to execute")

        # Make script executable
        os.chmod(self._temp_file, os.stat(self._temp_file).st_mode | 0o111)

        cmd = f"sh {self._temp_file}"
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

        # Join commands with && for sequential execution
        cmd = " && ".join(commands_list)
        self._run_command(cmd)

    def _run_command(self, cmd: str) -> None:
        """Run command with streaming output."""
        echo.info(f"Executing: {cmd}")

        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Stream stdout
        for line in process.stdout:
            echo.info(line.rstrip())

        # Stream stderr
        for line in process.stderr:
            echo.error(line.rstrip())

        # Wait for completion
        process.wait()

        if process.returncode != 0:
            raise RuntimeError(
                f"Command execution failed with exit code {process.returncode}"
            )

        echo.success("Execution completed successfully")

    def _cleanup(self) -> None:
        """Clean up temporary files."""
        if self._temp_file is not None and os.path.exists(self._temp_file):
            try:
                os.remove(self._temp_file)
                echo.debug(f"Cleaned up temp file: {self._temp_file}")
            except Exception:
                pass
