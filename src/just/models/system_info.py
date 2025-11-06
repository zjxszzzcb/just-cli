"""JUST CLI System Information Data Models"""

import json
import os
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional


@dataclass
class SystemInfo:
    """Store core system information"""
    platform: str  # e.g., "linux", "darwin", "windows"
    distro: str  # e.g., "ubuntu", "fedora", "macos", "windows"
    distro_version: str  # e.g., "22.04", "38", "14.2", "11"
    arch: str
    shell_name: str
    shell_profile: str
    path_configured: bool = False  # Default value during init


@dataclass
class PackageManager:
    """Store detected native package manager information"""
    name: str
    path: str
    command: str


@dataclass
class ToolStatus:
    """Store installation status of basic tools"""
    installed: bool
    path: Optional[str] = None


@dataclass
class SystemConfig:
    """Root structure of system_info.json"""
    system: SystemInfo
    pms: List[PackageManager]
    tools: Dict[str, ToolStatus]
    last_init_time: str

    def to_dict(self) -> dict:
        """Convert dataclass to dictionary for JSON serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'SystemConfig':
        """Create SystemConfig instance from dictionary"""
        # Convert nested objects
        system = SystemInfo(**data['system'])
        pms = [PackageManager(**pm) for pm in data['pms']]
        tools = {name: ToolStatus(**status) for name, status in data['tools'].items()}

        return cls(
            system=system,
            pms=pms,
            tools=tools,
            last_init_time=data['last_init_time']
        )

    def save_to_file(self, filepath: str) -> None:
        """Save configuration to file"""
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load_from_file(cls, filepath: str) -> Optional['SystemConfig']:
        """Load configuration from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except (FileNotFoundError, json.JSONDecodeError):
            return None