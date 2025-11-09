from typing import List, Literal

from just.utils.env_utils import EnvConfig


class JustConfig(EnvConfig):
    JUST_EDIT_USE_TOOL: Literal["textual", "edit", "unk"] = "unk"
    JUST_INSTALLER_SOURCES: List[str] = []
