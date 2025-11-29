import json

from just.utils.system_probe import SystemProbe


def probe_all() -> dict:
    """Probe all system information and return as a dictionary"""

    # Create system probe instance
    system_probe = SystemProbe()

    # Collect package managers information
    pms_probe = system_probe.pms
    pms_info = {
        "winget": {
            "version": pms_probe.winget.version,
            "path": pms_probe.winget.path,
            "command": pms_probe.winget.command,
            "available": pms_probe.winget.is_available()
        },
        "apt": {
            "version": pms_probe.apt.version,
            "path": pms_probe.apt.path,
            "command": pms_probe.apt.command,
            "available": pms_probe.apt.is_available()
        },
        "snap": {
            "version": pms_probe.snap.version,
            "path": pms_probe.snap.path,
            "command": pms_probe.snap.command,
            "available": pms_probe.snap.is_available()
        },
        "yum": {
            "version": pms_probe.yum.version,
            "path": pms_probe.yum.path,
            "command": pms_probe.yum.command,
            "available": pms_probe.yum.is_available()
        },
        "brew": {
            "version": pms_probe.brew.version,
            "path": pms_probe.brew.path,
            "command": pms_probe.brew.command,
            "available": pms_probe.brew.is_available()
        }
    }

    # Collect development tools information
    tools_probe = system_probe.tools
    tools_info = {
        "git": {
            "version": tools_probe.git.version,
            "path": tools_probe.git.path,
            "command": tools_probe.git.command,
            "available": tools_probe.git.is_available()
        },
        "docker": {
            "version": tools_probe.docker.version,
            "path": tools_probe.docker.path,
            "command": tools_probe.docker.command,
            "available": tools_probe.docker.is_available()
        },
        "docker_compose": {
            "version": tools_probe.docker_compose.version,
            "path": tools_probe.docker_compose.path,
            "command": tools_probe.docker_compose.command,
            "available": tools_probe.docker_compose.is_available()
        },
        "ssh": {
            "version": tools_probe.ssh.version,
            "path": tools_probe.ssh.path,
            "command": tools_probe.ssh.command,
            "available": tools_probe.ssh.is_available()
        },
        "curl": {
            "version": tools_probe.curl.version,
            "path": tools_probe.curl.path,
            "command": tools_probe.curl.command,
            "available": tools_probe.curl.is_available()
        },
        "wget": {
            "version": tools_probe.wget.version,
            "path": tools_probe.wget.path,
            "command": tools_probe.wget.command,
            "available": tools_probe.wget.is_available()
        },
        "tar": {
            "version": tools_probe.tar.version,
            "path": tools_probe.tar.path,
            "command": tools_probe.tar.command,
            "available": tools_probe.tar.is_available()
        },
        "unzip": {
            "version": tools_probe.unzip.version,
            "path": tools_probe.unzip.path,
            "command": tools_probe.unzip.command,
            "available": tools_probe.unzip.is_available()
        },
        "zip": {
            "version": tools_probe.zip.version,
            "path": tools_probe.zip.path,
            "command": tools_probe.zip.command,
            "available": tools_probe.zip.is_available()
        }
    }

    # Collect system information
    system_info = {
        "platform": system_probe.platform,
        "architecture": system_probe.arch,
        "distribution": system_probe.distro,
        "distribution_version": system_probe.distro_version
    }

    # Combine all information into a single dictionary
    result = {
        "system": system_info,
        "package_managers": pms_info,
        "development_tools": tools_info
    }

    return result

print(json.dumps(probe_all(), indent=2))