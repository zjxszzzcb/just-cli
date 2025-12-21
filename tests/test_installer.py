"""
Cloudflare Installer Test Suite
===============================

This module demonstrates and verifies the Cloudflare installer behavior.
The Cloudflare installer automatically detects the system environment
and uses the appropriate installation method.

Behavior Documentation
----------------------

1. **Package Manager Priority**: If winget (Windows) or brew (macOS) is
   available, the installer uses execute_commands for package manager.

2. **Binary Download Fallback**: When no package manager is available
   and on Linux x86_64, it downloads the binary directly.

3. **URL Pattern**: Binary URLs follow the pattern:
   `cloudflared-{platform}-{arch}` where:
   - platform: linux
   - arch: amd64 (for x86_64)
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ensure src is in path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from testing import describe, it, expect


@describe("Cloudflare Installer")
class CloudflareInstallerTests:
    """
    Cloudflare Installer
    ====================
    
    Provides automated installation of cloudflared CLI tool.
    Supports multiple platforms and installation methods.
    """
    
    @it("uses BinaryInstaller with linux-amd64 URL on Linux x86_64")
    def test_linux_installation(self):
        """
        Given: A Linux x86_64 system without package managers
        When: install_cloudflare() is called
        Then: BinaryInstaller is used with the correct URL pattern
        """
        mock_installer = MagicMock()
        mock_system = MagicMock()
        mock_system.platform = "linux"
        mock_system.arch = "x86_64"
        mock_system.pms.winget.is_available.return_value = False
        mock_system.pms.brew.is_available.return_value = False
        
        with patch('just.BinaryInstaller', mock_installer), \
             patch('just.system', mock_system):
            
            from just.installers.cloudflare.installer import install_cloudflare
            install_cloudflare()
            
            # Verify: BinaryInstaller called with correct URL
            expect(mock_installer.called).to_be_true()
            
            call_args = mock_installer.call_args
            url = call_args[0][0]
            kwargs = call_args[1]
            
            expect(url).to_contain("cloudflared-linux-amd64")
            expect(kwargs.get('alias')).to_equal("cloudflared")
            
            # Verify: run() was called
            mock_installer.return_value.run.assert_called_once()
    
    @it("uses winget on Windows when available")
    def test_windows_winget_installation(self):
        """
        Given: A Windows system with winget available
        When: install_cloudflare() is called
        Then: execute_commands with winget is called
        """
        mock_execute = MagicMock()
        mock_installer = MagicMock()
        mock_system = MagicMock()
        mock_system.platform = "windows"
        mock_system.arch = "x86_64"
        mock_system.pms.winget.is_available.return_value = True
        mock_system.pms.brew.is_available.return_value = False
        
        with patch('just.execute_commands', mock_execute), \
             patch('just.BinaryInstaller', mock_installer), \
             patch('just.system', mock_system):
            
            from just.installers.cloudflare.installer import install_cloudflare
            install_cloudflare()
            
            # Verify: execute_commands with winget was called
            mock_execute.assert_called_once()
            call_args = mock_execute.call_args[0][0]
            expect(call_args).to_contain("winget")
            expect(call_args).to_contain("Cloudflare.cloudflared")
            
            # Verify: BinaryInstaller was NOT called
            expect(mock_installer.called).to_be_false()
    
    @it("uses brew on macOS when available")
    def test_macos_brew_installation(self):
        """
        Given: A macOS system with Homebrew available
        When: install_cloudflare() is called
        Then: execute_commands with brew is called
        """
        mock_execute = MagicMock()
        mock_installer = MagicMock()
        mock_system = MagicMock()
        mock_system.platform = "darwin"
        mock_system.arch = "x86_64"
        mock_system.pms.winget.is_available.return_value = False
        mock_system.pms.brew.is_available.return_value = True
        
        with patch('just.execute_commands', mock_execute), \
             patch('just.BinaryInstaller', mock_installer), \
             patch('just.system', mock_system):
            
            from just.installers.cloudflare.installer import install_cloudflare
            install_cloudflare()
            
            # Verify: execute_commands with brew was called
            mock_execute.assert_called_once()
            call_args = mock_execute.call_args[0][0]
            expect(call_args).to_contain("brew install cloudflared")
            
            # Verify: BinaryInstaller was NOT called
            expect(mock_installer.called).to_be_false()
    
    @it("raises NotImplementedError for unsupported platforms")
    def test_unsupported_platform(self):
        """
        Given: A platform without winget/brew and not Linux x86_64
        When: install_cloudflare() is called
        Then: NotImplementedError is raised
        """
        mock_system = MagicMock()
        mock_system.platform = "freebsd"
        mock_system.arch = "arm64"
        mock_system.pms.winget.is_available.return_value = False
        mock_system.pms.brew.is_available.return_value = False
        
        with patch('just.system', mock_system):
            from just.installers.cloudflare.installer import install_cloudflare
            
            error_raised = False
            try:
                install_cloudflare()
            except NotImplementedError:
                error_raised = True
            
            expect(error_raised).to_be_true()


if __name__ == '__main__':
    from testing import run_tests
    success = run_tests()
    sys.exit(0 if success else 1)
