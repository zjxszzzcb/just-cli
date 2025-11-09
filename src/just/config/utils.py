"""JUST CLI Configuration Utility Functions"""

from pathlib import Path
from typing import Optional

from just.core.system_probe.system_info import SystemConfig


def get_config_dir() -> Path:
    """Get JUST configuration directory path"""
    home = Path.home()
    return home / ".just"


def ensure_config_dir_exists() -> Path:
    """Ensure JUST configuration directory exists, create if not"""
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def _get_system_info_file() -> Path:
    """Get system information configuration file path"""
    return get_config_dir() / "system_info.json"


def get_extensions_dir() -> Path:
    """Get user extensions directory path"""
    return get_config_dir() / "extensions"


def ensure_extensions_dir_exists() -> Path:
    """Ensure user extensions directory exists, create if not"""
    extensions_dir = get_extensions_dir()
    extensions_dir.mkdir(parents=True, exist_ok=True)
    return extensions_dir


def load_system_config() -> Optional[SystemConfig]:
    """Load system configuration"""
    config_file = _get_system_info_file()
    if config_file.exists():
        return SystemConfig.load_from_file(str(config_file))
    return None


def save_system_config(config: SystemConfig) -> None:
    """Save system configuration"""
    config_file = _get_system_info_file()
    config.save_to_file(str(config_file))


def is_initialized() -> bool:
    """Check if JUST is initialized"""
    config_file = _get_system_info_file()
    return config_file.exists()
