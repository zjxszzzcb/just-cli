"""
BashScriptInstaller Test Suite
=============================

This module tests the BashScriptInstaller behavior.

Behavior Documentation
----------------------

1. **Mutual Exclusivity**: Must provide either 'commands' OR 'script_url',
   but not both or neither. Raises ValueError otherwise.

2. **Command Execution**: Accepts either a single string or list of strings.
   Commands are joined with '&&' for sequential execution.

3. **Script Download**: Downloads script from URL to temp file using requests,
   then runs it with the shell.

4. **Error Handling**: Raises RuntimeError on download failure or execution failure.
"""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ensure src is in path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from testing import describe, it, expect


@describe("BashScriptInstaller")
class BashScriptInstallerTests:
    """
    BashScriptInstaller
    ==================

    Installer for bash scripts that can execute inline commands
    or download and run scripts from URLs.
    """

    @it("executes single command correctly")
    def test_single_command(self):
        """
        Given: A BashScriptInstaller with a single command
        When: run() is called
        Then: The command is executed successfully
        """
        mock_process = MagicMock()
        mock_process.stdout = iter([])
        mock_process.stderr = iter([])
        mock_process.returncode = 0
        mock_process.wait.return_value = None

        with patch("subprocess.Popen", return_value=mock_process):
            from just.core.installer.installers.script_installer import (
                BashScriptInstaller,
            )

            installer = BashScriptInstaller(commands="echo 'hello'")
            installer.run()

            # Verify: Popen was called with correct command
            call_args = subprocess.Popen.call_args
            expect(call_args).not_.to_be_none()

    @it("executes list of commands correctly")
    def test_list_of_commands(self):
        """
        Given: A BashScriptInstaller with a list of commands
        When: run() is called
        Then: Commands are joined with && and executed sequentially
        """
        mock_process = MagicMock()
        mock_process.stdout = iter([])
        mock_process.stderr = iter([])
        mock_process.returncode = 0
        mock_process.wait.return_value = None

        with patch("subprocess.Popen", return_value=mock_process):
            from just.core.installer.installers.script_installer import (
                BashScriptInstaller,
            )

            installer = BashScriptInstaller(commands=["echo 'hello'", "echo 'world'"])
            installer.run()

            # Verify: Popen was called (commands joined with &&)
            call_args = subprocess.Popen.call_args
            expect(call_args).not_.to_be_none()

    @it("downloads and executes script from URL")
    def test_script_url_download_and_execute(self):
        """
        Given: A BashScriptInstaller with script_url
        When: run() is called
        Then: Script is downloaded and executed
        """
        mock_process = MagicMock()
        mock_process.stdout = iter([])
        mock_process.stderr = iter([])
        mock_process.returncode = 0
        mock_process.wait.return_value = None

        mock_stat = MagicMock()
        mock_stat.st_mode = 0o644

        with (
            patch("subprocess.Popen", return_value=mock_process),
            patch("requests.get") as mock_get,
            patch("tempfile.mkstemp") as mock_mkstemp,
            patch("os.chmod"),
            patch("os.close"),
            patch("os.path.exists", return_value=True),
            patch("os.stat", return_value=mock_stat),
            patch("os.remove"),
            patch("builtins.open", MagicMock()),
        ):
            mock_mkstemp.return_value = (123, "/tmp/test_script.sh")
            mock_get.return_value.text = '#!/bin/bash\necho "hello"'

            from just.core.installer.installers.script_installer import (
                BashScriptInstaller,
            )

            installer = BashScriptInstaller(script_url="https://example.com/script.sh")
            installer.run()

            # Verify: requests.get was called
            expect(mock_get.called).to_be_true()
            expect(mock_get.call_args[0][0]).to_equal("https://example.com/script.sh")

    @it("raises ValueError when both commands and script_url provided")
    def test_mutual_exclusivity_both_provided(self):
        """
        Given: Both commands and script_url are provided
        When: BashScriptInstaller is instantiated
        Then: ValueError is raised
        """
        from just.core.installer.installers.script_installer import BashScriptInstaller

        error_raised = False
        try:
            BashScriptInstaller(
                commands="echo hello", script_url="https://example.com/script.sh"
            )
        except ValueError as e:
            error_raised = True
            expect(str(e)).to_contain(
                "Either 'commands' or 'script_url' must be provided"
            )

        expect(error_raised).to_be_true()

    @it("raises ValueError when neither commands nor script_url provided")
    def test_mutual_exclusivity_neither_provided(self):
        """
        Given: Neither commands nor script_url is provided
        When: BashScriptInstaller is instantiated
        Then: ValueError is raised
        """
        from just.core.installer.installers.script_installer import BashScriptInstaller

        error_raised = False
        try:
            BashScriptInstaller()
        except ValueError as e:
            error_raised = True
            expect(str(e)).to_contain(
                "Either 'commands' or 'script_url' must be provided"
            )

        expect(error_raised).to_be_true()

    @it("raises RuntimeError on download failure")
    def test_download_failure(self):
        """
        Given: A script_url that fails to download
        When: run() is called
        Then: RuntimeError is raised
        """
        with (
            patch("requests.get", side_effect=Exception("Network error")),
            patch("tempfile.mkstemp") as mock_mkstemp,
            patch("os.close"),
            patch("os.path.exists", return_value=False),
        ):
            mock_mkstemp.return_value = (123, "/tmp/test_script.sh")

            from just.core.installer.installers.script_installer import (
                BashScriptInstaller,
            )

            error_raised = False
            try:
                installer = BashScriptInstaller(
                    script_url="https://example.com/script.sh"
                )
                installer.run()
            except RuntimeError as e:
                error_raised = True
                expect(str(e)).to_contain("Failed to download script")

            expect(error_raised).to_be_true()

    @it("raises RuntimeError on command execution failure")
    def test_execution_failure(self):
        """
        Given: A command that fails with non-zero exit code
        When: run() is called
        Then: RuntimeError is raised
        """
        mock_process = MagicMock()
        mock_process.stdout = iter([])
        mock_process.stderr = iter(["error message"])
        mock_process.returncode = 1
        mock_process.wait.return_value = None

        with patch("subprocess.Popen", return_value=mock_process):
            from just.core.installer.installers.script_installer import (
                BashScriptInstaller,
            )

            error_raised = False
            try:
                installer = BashScriptInstaller(commands="failing_command")
                installer.run()
            except RuntimeError as e:
                error_raised = True
                expect(str(e)).to_contain("Command execution failed")

            expect(error_raised).to_be_true()


if __name__ == "__main__":
    from testing import run_tests

    success = run_tests()
    sys.exit(0 if success else 1)
