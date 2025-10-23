from typing import Literal

from .env_config import EnvConfig


class JustToolConfig(EnvConfig):
    JUST_EDIT_USE_TOOL: Literal["textual", "edit", "unk"] = "unk"