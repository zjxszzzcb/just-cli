import typer
import os
from pathlib import Path
from typing import List, Optional, Dict
from typing_extensions import Annotated
from urllib.parse import urlparse

from just import just_cli, capture_exception, echo
from just.utils import download_with_resume


def parse_headers(header_list: List[str]) -> Dict[str, str]:
    """Parse header list to dictionary."""
    if not header_list:
        return {}
    headers: Dict[str, str] = {}
    for header in header_list:
        if ':' in header:
            key, value = header.split(':', 1)
            headers[key.strip()] = value.strip()
    return headers


@just_cli.command(name="download")
@capture_exception
def download_command(
    url: Annotated[str, typer.Argument(
        help="URL to download",
        show_default=False
    )],
    headers: Annotated[Optional[List[str]], typer.Option(
        "-H", "--header",
        help="Custom headers (can be used multiple times)"
    )] = None,
    output: Annotated[Optional[str], typer.Option(
        "-o", "--output",
        help="Output filename"
    )] = None,
    verbose: Annotated[bool, typer.Option(
        "--verbose", "-v",
        help="Enable verbose logging"
    )] = False
) -> None:
    """
    Download a file from URL with resume support and custom headers.

    Examples:
    just download https://example.com/file.zip
    just download https://example.com/file.zip -H "Authorization: Bearer token" -H "User-Agent: MyApp/1.0"
    just download https://example.com/file.zip -o myfile.zip
    """
    # Parse headers
    parsed_headers = parse_headers(headers)

    # Determine output filename
    if output:
        output_file = output
    else:
        # Extract filename from URL
        parsed_url = urlparse(url)
        output_file = os.path.basename(parsed_url.path)
        if not output_file:
            output_file = "downloaded_file"

    # Ensure output directory exists
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    echo.info(
        f"Downloading {url} to {output_file}"
    )

    # Perform download with resume support
    success = download_with_resume(url, parsed_headers, output_file, verbose=verbose)

    if not success:
        raise Exception("Download failed")