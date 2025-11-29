import unittest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ensure src is in path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Import the installer function
# Note: We need to import just first to ensure configuration is loaded if needed
import just
from just.installers.cloudflare.installer import install_cloudflare

class TestCloudflareInstaller(unittest.TestCase):
    """
    Documentation for Cloudflare Installer
    ======================================
    
    This test suite demonstrates how the Cloudflare installer works.
    """

    @patch('just.SimpleReleaseInstaller')
    @patch('just.system')
    def test_windows_installation(self, mock_system, mock_installer_cls):
        """
        Scenario: Installing on Windows
        
        The installer should use SimpleReleaseInstaller with the correct URL and executable.
        """
        print("\n   Testing Cloudflare installation on Windows...")
        
        # Mock system info
        mock_system.platform = "windows"
        mock_system.arch = "amd64"
        
        # Mock installer instance
        mock_installer_instance = MagicMock()
        mock_installer_cls.return_value = mock_installer_instance
        
        # Run installer
        install_cloudflare()
        
        # Verify SimpleReleaseInstaller was called correctly
        mock_installer_cls.assert_called_once()
        call_args = mock_installer_cls.call_args
        
        # Check URL
        url = call_args[1]['url'] if 'url' in call_args[1] else call_args[0][0]
        self.assertIn("cloudflared-windows-amd64.exe", url)
        
        # Check executables
        executables = call_args[1]['executables']
        self.assertEqual(executables, ["cloudflared.exe"])
        
        # Verify run was called
        mock_installer_instance.run.assert_called_once()
        
        print("   ✅ Windows installation flow correct")

    @patch('just.download_with_resume')
    @patch('os.chmod')
    @patch('os.stat')
    @patch('just.system')
    @patch('just.config')
    def test_linux_installation(self, mock_config, mock_system, mock_stat, mock_chmod, mock_download):
        """
        Scenario: Installing on Linux
        
        The installer should download the binary directly and make it executable.
        """
        print("\n   Testing Cloudflare installation on Linux...")
        
        # Mock system info
        mock_system.platform = "linux"
        mock_system.arch = "x86_64"
        
        # Mock config directories
        mock_cache_dir = MagicMock()
        mock_bin_dir = MagicMock()
        mock_config.get_cache_dir.return_value = mock_cache_dir
        mock_config.get_config_dir.return_value = mock_bin_dir
        
        # Mock file operations
        mock_stat_result = MagicMock()
        mock_stat_result.st_mode = 0o644
        mock_stat.return_value = mock_stat_result
        
        # Run installer
        install_cloudflare()
        
        # Verify download
        mock_download.assert_called_once()
        args, _ = mock_download.call_args
        self.assertIn("cloudflared-linux-amd64", args[0])
        
        # Verify chmod
        mock_chmod.assert_called_once()
        
        print("   ✅ Linux installation flow correct")

if __name__ == '__main__':
    unittest.main()
