"""JUST CLI System Probing Core Functions"""
import platform
import shutil
import subprocess

from dataclasses import dataclass
from typing import Tuple, List, Dict, Literal, Optional


Platform = Literal["linux", "darwin", "windows"]
Arch = Literal["x86_64", "aarch64"]


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

@dataclass
class ToolStatus:
    version: str = ""
    path: Optional[str] = None
    command: Optional[str] = None

    def is_available(self) -> bool:
        return self.command is not None


def probe_tool(name: str) -> ToolStatus:
    """Probe basic tools"""
    # Check if the tool exists in the system path
    path = shutil.which(name)

    if path is None:
        # Tool does not exist
        return ToolStatus()

    # Tool exists, try to get version information
    version = ""
    # Try common arguments to get version information
    # Different tools may use different arguments to display version
    version_args = ["--version", "-v", "version"]

    for arg in version_args:
        try:
            # Use subprocess to get version output
            result = subprocess.run(
                [name, arg],
                capture_output=True,
                text=True,
                timeout=5  # 5 second timeout
            )
            if result.returncode == 0 and result.stdout:
                # Extract the first line of version information
                version = result.stdout.strip().split('\n')[0]
                break
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            # If one argument fails, continue trying the next
            continue

    # Return ToolStatus object
    return ToolStatus(version=version, path=path, command=name)



class SystemProbe:
    @property
    def arch(self) -> Arch:
        return get_arch()

    @property
    def platform(self) -> Platform:
        return get_platform()

    @property
    def distro(self) -> str:
        return get_distro_name_version(self.platform)[0]

    @property
    def distro_version(self) -> str:
        return get_distro_name_version(self.platform)[1]

    @property
    def pms(self):
        return PmsProbe()

    @property
    def tools(self):
        return DevToolProbe()


class PmsProbe:
    @property
    def winget(self) -> ToolStatus:
        return probe_tool("winget")

    @property
    def apt(self) -> ToolStatus:
        return probe_tool("apt")

    @property
    def snap(self) -> ToolStatus:
        return probe_tool("snap")

    @property
    def yum(self) -> ToolStatus:
        return probe_tool("yum")

    @property
    def brew(self) -> ToolStatus:
        return probe_tool("brew")


class DevToolProbe:
    @property
    def git(self) -> ToolStatus:
        return probe_tool("git")

    @property
    def docker(self) -> ToolStatus:
        return probe_tool("docker")

    @property
    def docker_compose(self) -> ToolStatus:
        return probe_tool("docker-compose")

    @property
    def ssh(self) -> ToolStatus:
        return probe_tool("ssh")

    @property
    def curl(self) -> ToolStatus:
        return probe_tool("curl")

    @property
    def wget(self) -> ToolStatus:
        return probe_tool("wget")

    @property
    def tar(self) -> ToolStatus:
        return probe_tool("tar")

    @property
    def unzip(self) -> ToolStatus:
        return probe_tool("unzip")

    @property
    def zip(self) -> ToolStatus:
        return probe_tool("zip")
