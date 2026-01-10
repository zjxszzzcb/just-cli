"""JUST CLI Configuration Utility Functions"""
from dotenv import load_dotenv, set_key
from pathlib import Path
from typing import Optional

from just.core.system_probe.system_info import SystemConfig
from just.utils.file_utils import write_file


def get_config_dir() -> Path:
    """Get JUST configuration directory path"""
    home = Path.home()
    return home / ".just"


def get_cache_dir() -> Path:
    """Get JUST cache directory path"""
    home = Path.home()
    return home / ".cache" / "just"


def ensure_config_dir_exists() -> Path:
    """Ensure JUST configuration directory exists, create if not"""
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_extension_dir() -> Path:
    """Get user extensions directory path"""
    return get_config_dir() / "extensions"


def get_command_dir() -> Path:
    """Get user commands directory path"""
    return Path(__file__).parent.parent.parent / "commands"


def get_basic_installer_dir() -> Path:
    """Get basic installer directory path"""
    return Path(__file__).parent.parent.parent / "installers"


def ensure_extensions_dir_exists() -> Path:
    """Ensure user extensions directory exists, create if not"""
    extensions_dir = get_extension_dir()
    extensions_dir.mkdir(parents=True, exist_ok=True)
    return extensions_dir


def get_env_config_file() -> Path:
    """Get JUST environment configuration file path"""
    return get_config_dir() / ".env"


def load_env_config():
    env_config_file = get_env_config_file()
    if not env_config_file.exists():
        ensure_config_dir_exists()
        write_file(str(env_config_file), "")
    load_dotenv(get_env_config_file())


def update_env_config(key: str, value: str):
    env_config_file = get_env_config_file()
    if not env_config_file.exists():
        ensure_config_dir_exists()
        write_file(str(env_config_file), "")
    set_key(get_env_config_file(), key, value)


def _get_system_info_file() -> Path:
    """Get system information configuration file path"""
    return get_config_dir() / "system_info.json"


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