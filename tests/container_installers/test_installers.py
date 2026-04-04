"""
Installer Container Integration Tests
======================================

This module contains comprehensive integration tests for all 11 installers.
Tests verify that installers can be executed in a container environment and
successfully install tools using their respective verification commands.

Usage:
    python tests/container_installers/test_installers.py

Test Framework:
    Uses custom testing.py framework (describe/it/expect API) - NOT pytest

Verification Strategy:
    1. Import installer module
    2. Call installer function
    3. Execute verification command
    4. Check for PASS/FAIL status
"""

import sys
import subprocess
from pathlib import Path

# Ensure src and tests are in path
tests_dir = Path(__file__).parent.parent
sys.path.insert(0, str(tests_dir / "src"))
sys.path.insert(0, str(tests_dir))

from testing import describe, it, expect


# =============================================================================
# Configuration
# =============================================================================

SKIPPED_INSTALLERS = [
    "brew",  # macOS only
    "clash",  # Requires subscription
    "tailscale",  # Requires login
    "docker",  # Requires root
]

# Define installer configurations
# Each config specifies the module path, function name, and verification command
INSTALLER_CONFIGS = {
    "cloudflare": {
        "module_path": "just.installers.cloudflare.installer",
        "function_name": "install_cloudflare",
        "verify_command": "cloudflared --version",
    },
    "uv": {
        "module_path": "just.installers.uv.installer",
        "function_name": "install_uv",
        "verify_command": "uv --version",
    },
    "miniconda3": {
        "module_path": "just.installers.miniconda3.installer",
        "function_name": "install_miniconda3",
        "verify_command": "conda --version",
    },
    "opencode": {
        "module_path": "just.installers.opencode.installer",
        "function_name": "install_opencode",
        "verify_command": "opencode --version",
    },
    "gh": {
        "module_path": "just.installers.gh.installer",
        "function_name": "install_gh",
        "verify_command": "gh --version",
    },
    "openclaw": {
        "module_path": "just.installers.openclaw.installer",
        "function_name": "install_openclaw",
        "verify_command": "openclaw --version",
    },
    "edit": {
        "module_path": "just.installers.edit.installer",
        "function_name": "install_edit",
        "verify_command": "edit --version",
    },
    "claude-code": {
        "module_path": "just.installers.claude_code.installer",
        "function_name": "install_claude_code",
        "verify_command": "claude --version",
    },
    "qodercli": {
        "module_path": "just.installers.qodercli.installer",
        "function_name": "install_qodercli",
        "verify_command": "qodercli --version",
    },
    "nvm": {
        "module_path": "just.installers.nvm.installer",
        "function_name": "install_nvm",
        "verify_command": "source ~/.nvm/nvm.sh && nvm --version",
    },
    "mssh": {
        "module_path": "just.installers.mssh.installer",
        "function_name": "install_nvm",
        "verify_command": "pip show ssh-manager",
    },
}


def run_single_installer_test(installer_name: str) -> bool:
    """
    Run a single installer test.

    Steps:
        1. Import installer module
        2. Call installer function
        3. Execute verification command
        4. Return True if verification succeeds, False otherwise

    Args:
        installer_name: Name of installer to test (must be in INSTALLER_CONFIGS)

    Returns:
        True if installation and verification succeed, False otherwise
    """
    if installer_name not in INSTALLER_CONFIGS:
        raise ValueError(f"Unknown installer: {installer_name}")

    config = INSTALLER_CONFIGS[installer_name]

    try:
        # Step 1: Import installer module
        module = __import__(config["module_path"], fromlist=[""])

        # Step 2: Call installer function
        installer_func = getattr(module, config["function_name"])
        installer_func()

        # Step 3: Execute verification command
        result = subprocess.run(
            config["verify_command"],
            shell=True,
            capture_output=True,
            text=True,
            timeout=120,
        )

        # Step 4: Return result status
        return result.returncode == 0

    except Exception as e:
        print(f"Error testing {installer_name}: {e}")
        return False


# =============================================================================
# Test Suites
# =============================================================================


@describe("Installer Container Integration Tests")
class InstallerContainerTests:
    """
    Installer Container Integration Tests
    =====================================

    Comprehensive tests for 11 installers in container environment.
    Tests verify actual installation success using version commands.
    """

    @it("tests all non-skipped installers")
    def test_all_installers(self):
        """
        Given: A container with just-cli installed
        When: All non-skipped installers are tested
        Then: Each installer successfully installs and verifies
        """
        # Test all installers except skipped ones
        for installer_name in INSTALLER_CONFIGS:
            if installer_name in SKIPPED_INSTALLERS:
                print(f"Skipping {installer_name} (OS-specific or requires auth)")
                continue

            # Run installer test
            success = run_single_installer_test(installer_name)

            # Verify installation succeeded
            expect(success).to_be_true()
            print(f"✓ {installer_name} installation successful")


@describe("Cloudflare Installer")
class CloudflareInstallerTests:
    """
    Cloudflare Installer
    ====================

    Tests installation of Cloudflare Tunnel client (cloudflared).
    """

    @it("installs cloudflared successfully")
    def test_install_cloudflared(self):
        """
        Given: A container with just-cli installed
        When: install_cloudflare() is called
        Then: cloudflared --version command succeeds
        """
        success = run_single_installer_test("cloudflare")
        expect(success).to_be_true()


@describe("UV Installer")
class UVInstallerTests:
    """
    UV Installer
    ============

    Tests installation of uv Python package manager.
    """

    @it("installs uv successfully")
    def test_install_uv(self):
        """
        Given: A container with just-cli installed
        When: install_uv() is called
        Then: uv --version command succeeds
        """
        success = run_single_installer_test("uv")
        expect(success).to_be_true()


@describe("Miniconda3 Installer")
class Miniconda3InstallerTests:
    """
    Miniconda3 Installer
    ====================

    Tests installation of Miniconda3 Python distribution.
    """

    @it("installs miniconda3 successfully")
    def test_install_miniconda3(self):
        """
        Given: A container with just-cli installed
        When: install_miniconda3() is called
        Then: conda --version command succeeds
        """
        success = run_single_installer_test("miniconda3")
        expect(success).to_be_true()


@describe("OpenCode Installer")
class OpenCodeInstallerTests:
    """
    OpenCode Installer
    ==================

    Tests installation of OpenCode AI coding agent.
    """

    @it("installs opencode successfully")
    def test_install_opencode(self):
        """
        Given: A container with just-cli installed
        When: install_opencode() is called
        Then: opencode --version command succeeds
        """
        success = run_single_installer_test("opencode")
        expect(success).to_be_true()


@describe("GitHub CLI Installer")
class GHInstallerTests:
    """
    GitHub CLI Installer
    ====================

    Tests installation of GitHub CLI (gh).
    """

    @it("installs gh successfully")
    def test_install_gh(self):
        """
        Given: A container with just-cli installed
        When: install_gh() is called
        Then: gh --version command succeeds
        """
        success = run_single_installer_test("gh")
        expect(success).to_be_true()


@describe("OpenClaw Installer")
class OpenClawInstallerTests:
    """
    OpenClaw Installer
    ==================

    Tests installation of OpenClaw personal AI assistant.
    """

    @it("installs openclaw successfully")
    def test_install_openclaw(self):
        """
        Given: A container with just-cli installed
        When: install_openclaw() is called
        Then: openclaw --version command succeeds
        """
        success = run_single_installer_test("openclaw")
        expect(success).to_be_true()


@describe("Edit Installer")
class EditInstallerTests:
    """
    Edit Installer
    ==============

    Tests installation of Edit text editor.
    """

    @it("installs edit successfully")
    def test_install_edit(self):
        """
        Given: A container with just-cli installed
        When: install_edit() is called
        Then: edit --version command succeeds
        """
        success = run_single_installer_test("edit")
        expect(success).to_be_true()


@describe("Claude Code Installer")
class ClaudeCodeInstallerTests:
    """
    Claude Code Installer
    =====================

    Tests installation of Claude Code CLI.
    """

    @it("installs claude-code successfully")
    def test_install_claude_code(self):
        """
        Given: A container with just-cli installed
        When: install_claude_code() is called
        Then: claude --version command succeeds
        """
        success = run_single_installer_test("claude-code")
        expect(success).to_be_true()


@describe("Qoder CLI Installer")
class QoderCLIInstallerTests:
    """
    Qoder CLI Installer
    ===================

    Tests installation of Qoder CLI tool.
    """

    @it("installs qodercli successfully")
    def test_install_qodercli(self):
        """
        Given: A container with just-cli installed
        When: install_qodercli() is called
        Then: qodercli --version command succeeds
        """
        success = run_single_installer_test("qodercli")
        expect(success).to_be_true()


@describe("NVM Installer")
class NVMInstallerTests:
    """
    NVM Installer
    =============

    Tests installation of Node Version Manager (nvm).
    Requires sourcing ~/.nvm/nvm.sh before running nvm --version.
    """

    @it("installs nvm successfully")
    def test_install_nvm(self):
        """
        Given: A container with just-cli installed
        When: install_nvm() is called
        Then: source ~/.nvm/nvm.sh && nvm --version command succeeds
        """
        success = run_single_installer_test("nvm")
        expect(success).to_be_true()


@describe("MSSH Installer")
class MSSHInstallerTests:
    """
    MSSH Installer
    ==============

    Tests installation of TUI SSH Manager (ssh-manager).
    """

    @it("installs mssh successfully")
    def test_install_mssh(self):
        """
        Given: A container with just-cli installed
        When: install_nvm() is called (installer function name)
        Then: pip show ssh-manager command succeeds
        """
        success = run_single_installer_test("mssh")
        expect(success).to_be_true()


# =============================================================================
# Standalone Execution
# =============================================================================

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
