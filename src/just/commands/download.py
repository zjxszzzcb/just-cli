import typer
from typing import List, Optional, Dict
from typing_extensions import Annotated

from just import just_cli, capture_exception
from just.utils import download_with_resume


def parse_headers(header_list: Optional[List[str]]) -> Optional[Dict[str, str]]:
    """Parse header list to dictionary."""
    if not header_list:
        return None
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
    if not download_with_resume(
        url=url,
        headers=parse_headers(headers),
        output_file=output,
        verbose=verbose
    ):
        raise Exception("Download failed")
