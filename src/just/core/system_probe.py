"""JUST CLI System Probing Core Functions"""

import platform
import os
import shutil
from datetime import datetime, timezone
from typing import Tuple, List, Dict
from just.models.system_info import SystemInfo, PackageManager, ToolStatus, SystemConfig


def get_arch() -> str:
    """Normalize architecture name"""
    machine = platform.machine().lower()
    if machine in ("x86_64", "amd64"):
        return "amd64"
    if machine in ("aarch64", "arm64"):
        return "arm64"
    return machine


def get_platform_info() -> Tuple[str, str, str]:
    """Probe Platform, Distro, and Version"""
    sys_name = platform.system().lower()

    if sys_name == "linux":
        # Try to use 'distro' library (if installed)
        try:
            import distro
            return "linux", distro.id(), distro.version()
        except ImportError:
            # Fallback to /etc/os-release (simple parsing)
            try:
                with open("/etc/os-release") as f:
                    data = dict(line.strip().split('=', 1) for line in f if '=' in line)
                    distro_name = data.get('ID', 'linux').strip('"')
                    ver = data.get('VERSION_ID', 'unknown').strip('"')
                    return "linux", distro_name, ver
            except FileNotFoundError:
                return "linux", "unknown-linux", "unknown"

    elif sys_name == "darwin":  # macOS
        mac_ver = platform.mac_ver()
        return "darwin", "macos", mac_ver[0]

    elif sys_name == "windows":
        win_ver = platform.version()  # e.g., '10.0.19045'
        return "windows", "windows", win_ver

    return sys_name, "unknown", "unknown"


def get_shell_info() -> Tuple[str, str, bool]:
    """Probe Shell and Profile"""
    shell_path = os.environ.get("SHELL")
    if not shell_path:
        if platform.system() == "Windows":
            # Simplified assumption: prefer PowerShell on Windows
            # Real implementation needs to check $PROFILE
            return "powershell", "$PROFILE", False
        return "unknown", "unknown", False

    shell_name = os.path.basename(shell_path)
    home = os.path.expanduser("~")

    if shell_name == "bash":
        profile_path = os.path.join(home, ".bashrc")
    elif shell_name == "zsh":
        profile_path = os.path.join(home, ".zshrc")
    elif shell_name == "fish":
        profile_path = os.path.join(home, ".config", "fish", "config.fish")
    else:
        # Fallback for other shells
        profile_path = os.path.join(home, f".{shell_name}_profile")  # Guess

    # TODO: Real 'path_configured' needs to parse profile file
    # During init, we always assume it's False unless we find configuration
    path_configured = False

    return shell_name, profile_path, path_configured


def probe_pms() -> List[PackageManager]:
    """Probe available package managers"""
    detected_pms = []

    # (name, sudo_required)
    pms_to_check = {
        "apt": True,
        "yum": True,
        "dnf": True,
        "pacman": True,
        "brew": False,
        "winget": False,
        "choco": False,
        "scoop": False
    }

    for name, sudo in pms_to_check.items():
        path = shutil.which(name)
        if path:
            command = f"sudo {name}" if sudo and platform.system() != "Windows" else name
            detected_pms.append(PackageManager(name=name, path=path, command=command))

    return detected_pms


def probe_tools() -> Dict[str, ToolStatus]:
    """Probe basic tools"""
    detected_tools = {}
    tools_to_check = ["wget", "curl", "git", "docker", "tar", "unzip"]

    for name in tools_to_check:
        path = shutil.which(name)
        if path:
            detected_tools[name] = ToolStatus(installed=True, path=path)
        else:
            detected_tools[name] = ToolStatus(installed=False, path=None)

    return detected_tools


def probe_and_initialize_config() -> 'SystemConfig':
    """
    Probe the current system environment and return an instantiated SystemConfig object.
    """
    # 1. Probe system
    plat, distro, ver = get_platform_info()
    arch = get_arch()
    shell_name, shell_profile, path_configured = get_shell_info()

    system_info = SystemInfo(
        platform=plat,
        distro=distro,
        distro_version=ver,
        arch=arch,
        shell_name=shell_name,
        shell_profile=shell_profile,
        path_configured=path_configured  # Should be False during init
    )

    # 2. Probe PMs
    pms_list = probe_pms()

    # 3. Probe Tools
    tools_dict = probe_tools()

    # 4. Timestamp
    timestamp = datetime.now(timezone.utc).isoformat()

    # 5. Assemble Config object
    config = SystemConfig(
        system=system_info,
        pms=pms_list,
        tools=tools_dict,
        last_init_time=timestamp
    )

    return config