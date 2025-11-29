import os

from .base import JustInstallerSource
from .http import JustInstallerHttpSource
from .local import JustInstallerLocalSource


def fetch_installer_source(source_url) -> JustInstallerSource:
    # Convert Path objects to string if needed
    source_url_str = str(source_url) if hasattr(source_url, '__str__') else source_url

    if os.path.exists(source_url_str):
        return JustInstallerLocalSource(source_url_str)
    elif source_url_str.startswith('http'):
        return JustInstallerHttpSource(source_url_str)
    else:
        raise ValueError(f"Invalid source: {source_url_str}")