"""JUST CLI System Probing Core Functions"""

import platform
import os
import shutil

from datetime import datetime, timezone
from typing import Tuple, List, Dict

from just.core.system_probe.system_info import (
    Arch,
    Platform,
    SystemInfo,
    PackageManager,
    ToolStatus,
    SystemConfig
)


def get_arch() -> Arch:
    """Normalize architecture name"""
    machine = platform.machine().lower()
    if machine in ("x86_64", "amd64"):
        return "x86_64"
    if machine in ("aarch64", "arm64"):
        return "aarch64"
    raise NotImplementedError(f"Unsupported architecture {machine}")


def get_platform() -> Platform:
    """Normalize platform name"""
    sys_name = platform.system().lower()
    if sys_name in ("linux", "darwin", "windows"):
        return sys_name
    raise NotImplementedError(f"Unsupported platform {sys_name}")


def get_distro_name_version(plat: Platform) -> Tuple[str, str]:
    """Probe Platform, Distro, and Version"""
    plat = plat or get_platform()

    if plat == "linux":
        return get_distro_name_version_for_linux()

    elif plat == "darwin":
        return get_distro_name_version_for_darwin()

    elif plat == "windows":
        return get_distro_name_version_for_windows()

    else:
        raise NotImplementedError(f"Unsupported platform {plat}")


def get_distro_name_version_for_linux() -> Tuple[str, str]:
    try:
        import distro
        return distro.id(), distro.version()
    except ImportError:
        # Fallback to /etc/os-release (simple parsing)
        try:
            with open("/etc/os-release") as f:
                data = dict(line.strip().split('=', 1) for line in f if '=' in line)
                distro_name = data.get('ID', 'linux').strip('"')
                ver = data.get('VERSION_ID', 'unknown').strip('"')
                return distro_name, ver
        except FileNotFoundError:
            raise RuntimeError("Failed to import distro or find /etc/os-release")


def get_distro_name_version_for_darwin() -> Tuple[str, str]:
    try:
        return "macos", str(platform.mac_ver())
    except Exception:
        raise RuntimeError("Failed to get distro name version")


def get_distro_name_version_for_windows() -> Tuple[str, str]:
    version = platform.version()
    version_parts = list(map(int, version.split('.')))

    if version_parts[0] == 10:
        if version_parts[2] >= 22000:  # Windows 11开始于build 22000
            return "windows", "11"
        else:
            return "windows", "10"
    else:
        return "windows", version


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
    plat = get_platform()
    distro, ver = get_distro_name_version(plat)
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