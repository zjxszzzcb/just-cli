#!/usr/bin/env python3
"""
Test script for the init command functionality.
"""

import sys
import tempfile
from pathlib import Path

# Add the src directory to the path so we can import just modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from just.core.system_probe.system_info import SystemConfig, SystemInfo, PackageManager, ToolStatus
from just.core.system_probe.system_probe import probe_and_initialize_config
from just.core.config.utils import get_config_dir, ensure_config_dir_exists, save_system_config, load_system_config, is_initialized


def test_data_models():
    """Test the data models functionality."""
    print("Testing data models...")

    # Create test data
    system_info = SystemInfo(
        platform="linux",
        distro="ubuntu",
        distro_version="22.04",
        arch="amd64",
        shell_name="bash",
        shell_profile="/home/user/.bashrc",
        path_configured=False
    )

    pm = PackageManager(name="apt", path="/usr/bin/apt", command="sudo apt")
    tool_status = ToolStatus(installed=True, path="/usr/bin/curl")

    config = SystemConfig(
        system=system_info,
        pms=[pm],
        tools={"curl": tool_status},
        last_init_time="2023-01-01T00:00:00Z"
    )

    # Test serialization
    config_dict = config.to_dict()
    assert config_dict["system"]["platform"] == "linux"
    assert config_dict["pms"][0]["name"] == "apt"
    assert config_dict["tools"]["curl"]["installed"] == True

    # Test deserialization
    restored_config = SystemConfig.from_dict(config_dict)
    assert restored_config.system.platform == "linux"
    assert restored_config.pms[0].name == "apt"
    assert restored_config.tools["curl"].installed == True

    print("✅ Data models test passed")


def test_config_utils():
    """Test the config utilities functionality."""
    print("Testing config utilities...")

    # Test getting config directory
    config_dir = get_config_dir()
    assert isinstance(config_dir, Path)
    assert str(config_dir).endswith(".just")

    # Test checking initialization status
    # Note: _get_system_info_file is private, so we test is_initialized instead
    initialized = is_initialized()
    assert isinstance(initialized, bool)

    print("✅ Config utilities test passed")


def test_system_probe():
    """Test the system probe functionality."""
    print("Testing system probe...")

    # Test probing system configuration
    config = probe_and_initialize_config()

    # Basic validation
    assert config.system.platform is not None
    assert config.system.arch is not None
    assert isinstance(config.pms, list)
    assert isinstance(config.tools, dict)
    assert config.last_init_time is not None

    print("✅ System probe test passed")


def test_save_load_config():
    """Test saving and loading configuration."""
    print("Testing save/load configuration...")

    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Mock the config directory
        original_get_config_dir = get_config_dir
        def mock_get_config_dir():
            return Path(temp_dir) / ".just"

        # Patch the function
        from just.core.config import utils as just_config_utils
        just_config_utils.get_config_dir = mock_get_config_dir

        try:
            # Create test data
            system_info = SystemInfo(
                platform="test",
                distro="test",
                distro_version="1.0",
                arch="test",
                shell_name="test",
                shell_profile="test",
                path_configured=False
            )

            config = SystemConfig(
                system=system_info,
                pms=[],
                tools={},
                last_init_time="2023-01-01T00:00:00Z"
            )

            # Test saving
            save_system_config(config)

            # Test loading
            loaded_config = load_system_config()
            assert loaded_config is not None
            assert loaded_config.system.platform == "test"

            # Test is_initialized
            assert is_initialized() == True

        finally:
            # Restore the original function
            from just.core.config import utils as just_config_utils
            just_config_utils.get_config_dir = original_get_config_dir

    print("✅ Save/load configuration test passed")


def run_all_tests():
    """Run all tests."""
    print("Running init command tests...\n")

    tests = [
        test_data_models,
        test_config_utils,
        test_system_probe,
        test_save_load_config
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)