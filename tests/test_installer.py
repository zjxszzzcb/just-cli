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



    @patch('just.BinaryInstaller')
    @patch('just.system')
    def test_linux_installation(self, mock_system, mock_installer_cls):
        """
        Scenario: Installing on Linux
        
        The installer should use BinaryInstaller with the correct URL and alias.
        """
        print("\n   Testing Cloudflare installation on Linux...")
        
        # Mock system info
        mock_system.platform = "linux"
        mock_system.arch = "x86_64"
        # Ensure package managers are not available so it falls back to direct download
        mock_system.pms.winget.is_available.return_value = False
        mock_system.pms.brew.is_available.return_value = False
        
        # Mock installer instance
        mock_installer_instance = MagicMock()
        mock_installer_cls.return_value = mock_installer_instance
        
        # Run installer
        install_cloudflare()
        
        # Verify BinaryInstaller was called correctly
        mock_installer_cls.assert_called_once()
        call_args = mock_installer_cls.call_args
        
        # Check URL
        url = call_args[0][0]
        self.assertIn("cloudflared-linux-amd64", url)
        
        # Check alias
        alias = call_args[1]['alias']
        self.assertEqual(alias, "cloudflared")
        
        # Verify run was called
        mock_installer_instance.run.assert_called_once()
        
        print("   ✅ Linux installation flow correct")

if __name__ == '__main__':
    unittest.main()
