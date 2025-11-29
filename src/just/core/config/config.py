from typing import List

from just.utils.env_utils import EnvConfig


class JustConfig(EnvConfig):
    JUST_INSTALLER_SOURCES: List[str] = []
