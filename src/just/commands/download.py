import httpx
import typer
import os
from pathlib import Path
from typing import List, Optional

from just import just_cli, capture_exception, echo
from just.utils.progress import progress_bar


def parse_headers(header_list: List[str]) -> dict:
    """Parse header list to dictionary."""
    headers = {}
    for header in header_list:
        if ':' in header:
            key, value = header.split(':', 1)
            headers[key.strip()] = value.strip()
    return headers


def download_with_resume(
    url: str,
    headers: dict,
    output_file: str,
    chunk_size: int = 65536,
    force_simple_progress: bool = False,
    debug: bool = False
):
    """
    Download file with resume support and unified progress bar.

    Args:
        url: URL to download
        headers: Custom headers
        output_file: Output file path
        chunk_size: Chunk size for downloading
        force_simple_progress: Force simple text progress bar
        debug: Enable debug logging
    """
    if debug:
        echo.info(f"[DEBUG] Starting download: {url}")
        echo.info(f"[DEBUG] Output file: {output_file}")
        echo.info(f"[DEBUG] Chunk size: {chunk_size}")

    # Check if file already exists for resuming
    first_byte = 0
    mode = "wb"
    if os.path.exists(output_file):
        first_byte = os.path.getsize(output_file)
        mode = "ab"
        if debug:
            echo.info(f"[DEBUG] Found existing file: {first_byte} bytes, mode: {mode}")

    # Prepare headers for initial request
    request_headers = headers.copy()
    # Add Range header if resuming
    if first_byte > 0:
        request_headers['Range'] = f'bytes={first_byte}-'
        if debug:
            echo.info(f"[DEBUG] Added Range header: {request_headers['Range']}")

    try:
        if debug:
            echo.info(f"[DEBUG] Making initial request with headers: {request_headers}")

        with httpx.stream("GET", url, headers=request_headers, follow_redirects=True, timeout=30.0) as response:
            if debug:
                echo.info(f"[DEBUG] Initial response status: {response.status_code}")
                echo.info(f"[DEBUG] Response headers: {dict(response.headers)}")

            response.raise_for_status()

            # Check if server supports range requests
            if first_byte > 0 and response.status_code != 206:
                if debug:
                    echo.info(
                        f"[DEBUG] Server doesn't support range requests (status: {response.status_code}), "
                        f"restarting download")

                # Server doesn't support range requests, start from beginning
                # Need to make a new request without the Range header
                first_byte = 0
                mode = "wb"

                # Close the current stream and make a new request
                response.close()

                if debug:
                    echo.info(f"[DEBUG] Making fresh request without Range header")

                # Make a new request without the Range header
                with httpx.stream("GET", url, headers=headers, follow_redirects=True, timeout=30.0) as new_response:
                    if debug:
                        echo.info(f"[DEBUG] Fresh response status: {new_response.status_code}")

                    new_response.raise_for_status()
                    response = new_response

                    # Get total file size for fresh download
                    total_size = int(response.headers.get('content-length', 0))
                    if debug:
                        echo.info(f"[DEBUG] Fresh download total size: {total_size}")

                    # Download file with fresh start
                    return _download_stream(
                        response,
                        output_file,
                        total_size,
                        mode,
                        force_simple_progress,
                        first_byte,
                        chunk_size,
                        debug
                    )
            else:
                # Server supports range requests or it's a fresh download
                # Get total file size
                total_size = first_byte
                if response.status_code == 206:
                    # Partial content
                    content_range = response.headers.get('content-range', '')
                    if content_range.startswith('bytes '):
                        range_info = content_range[6:]  # Remove 'bytes ' prefix
                        if '/' in range_info:
                            _, total_size_str = range_info.split('/')
                            if total_size_str.isdigit():
                                total_size = int(total_size_str)
                    if debug:
                        echo.info(f"[DEBUG] Partial content (206), content-range: {content_range}, total size: {total_size}")
                elif response.status_code == 200:
                    # Full content
                    total_size = int(response.headers.get('content-length', 0))
                    if debug:
                        echo.info(f"[DEBUG] Full content (200), total size: {total_size}")
                else:
                    echo.error(f"HTTP {response.status_code}: {response.text}")
                    return False

                # Download file with resume support
                return _download_stream(response, output_file, total_size, mode, force_simple_progress, first_byte, chunk_size, debug)

    except Exception as e:
        echo.error(f"Download failed: {str(e)}")
        return False


def _download_stream(response, output_file: str, total_size: int, mode: str, force_simple_progress: bool, first_byte: int, chunk_size: int = 65536, debug: bool = False):
    """
    Helper function to download file stream.

    Args:
        response: HTTP response stream
        output_file: Output file path
        total_size: Total file size
        mode: File open mode ("wb" or "ab")
        force_simple_progress: Force simple text progress bar
        first_byte: Starting byte position
        chunk_size: Chunk size for downloading
        debug: Enable debug logging
    """
    if debug:
        echo.info(f"[DEBUG] Starting _download_stream: total_size={total_size}, mode={mode}, first_byte={first_byte}")

    # Determine progress bar mode
    progress_mode = "simple" if force_simple_progress else "auto"

    # Download file with unified progress bar
    downloaded = first_byte
    bytes_written = 0

    if debug:
        echo.info(f"[DEBUG] Opening file {output_file} with mode {mode}")

    with open(output_file, mode) as f:
        with progress_bar(total=total_size, desc="Downloading", unit="b", mode=progress_mode) as pbar:
            # Update progress for already downloaded bytes
            pbar.n = first_byte
            pbar.refresh()  # Force refresh to show correct initial position
            if debug:
                echo.info(f"[DEBUG] Progress bar initialized with n={first_byte}")

            for i, chunk in enumerate(response.iter_bytes(chunk_size=chunk_size)):
                if chunk:
                    f.write(chunk)
                    bytes_written += len(chunk)
                    downloaded += len(chunk)
                    pbar.update(len(chunk))

                    if debug and (i % 10 == 0 or len(chunk) < chunk_size):  # Log every 10 chunks or last chunk
                        echo.info(f"[DEBUG] Chunk {i}: wrote {len(chunk)} bytes, total written: {bytes_written}")

    if debug:
        echo.info(f"[DEBUG] Download completed: {output_file}, total bytes written: {bytes_written}")

    echo.info(f"Download completed: {output_file}")
    return True


@just_cli.command(name="download", help="Download file with resume support and custom headers.")
@capture_exception
def download_command(
    url: str,
    headers: List[str] = typer.Option([], "-H", "--header", help="Custom headers (can be used multiple times)"),
    output: Optional[str] = typer.Option(None, "-o", "--output", help="Output filename"),
    force_simple_progress: bool = typer.Option(False, "--force-simple-progress", help="Force simple text progress bar"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug logging")
):
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
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        output_file = os.path.basename(parsed_url.path)
        if not output_file:
            output_file = "downloaded_file"

    # Ensure output directory exists
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    echo.info(f"Downloading {url} to {output_file}")

    # Perform download with resume support
    success = download_with_resume(url, parsed_headers, output_file, force_simple_progress=force_simple_progress, debug=debug)

    if not success:
        raise Exception("Download failed")