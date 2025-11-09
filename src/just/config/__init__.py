from typing import Literal

from .env_config import EnvConfig
from .utils import ensure_config_dir_exists, save_system_config, is_initialized


class JustConfig(EnvConfig):
    JUST_EDIT_USE_TOOL: Literal["textual", "edit", "unk"] = "unk"


__all__ = [
    "JustConfig",
    "ensure_config_dir_exists",
    "save_system_config",
    "is_initialized",
]
