"""JUST CLI System Probing Core Functions"""

import platform
import os
import shutil

from datetime import datetime, timezone
from typing import Tuple, List, Dict, Literal

from just.core.system_probe.system_info import SystemInfo, PackageManager, ToolStatus, SystemConfig


def get_arch() -> Literal["x86_64", "aarch64"]:
    """Normalize architecture name"""
    machine = platform.machine().lower()
    if machine in ("x86_64", "amd64"):
        return "x86_64"
    if machine in ("aarch64", "arm64"):
        return "aarch64"
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
        # Get more accurate Windows version
        win_ver = platform.version()  # e.g., '10.0.19045'
        try:
            import subprocess
            # Use ver command to get Windows version
            result = subprocess.run(["ver"], capture_output=True, text=True, shell=True, timeout=5, encoding='utf-8', errors='ignore')
            if result.returncode == 0 and result.stdout:
                # Extract version from output like "Microsoft Windows [Version 10.0.22621.2506]"
                import re
                match = re.search(r'\[.*?([\d\.]+)\]', result.stdout)
                if match:
                    full_ver = match.group(1)  # e.g., "10.0.22621.2506"
                    # Determine if it's Windows 10 or 11 based on build number
                    # Windows 11 typically starts with build 22000 or higher
                    version_parts = full_ver.split(".")
                    if len(version_parts) >= 3:
                        try:
                            build_number = int(version_parts[2])  # Get build number
                            if build_number >= 22000:
                                # Use "11" as distro_version for Windows 11
                                return "windows", "windows", "11"
                            else:
                                # Use "10" as distro_version for Windows 10
                                return "windows", "windows", "10"
                        except ValueError:
                            pass
                    # If we can't determine build number, return simplified version
                    # Extract major version from full version (first part before the dot)
                    if "." in full_ver:
                        major_ver = full_ver.split(".")[0]
                        if major_ver == "10":
                            # For Windows, major version 10 could be Windows 10 or 11
                            # We'll use the build number approach or default to "10"
                            return "windows", "windows", "10"
                    return "windows", "windows", full_ver
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, ImportError, ValueError, IndexError):
            pass
        # Fallback to platform.version()
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