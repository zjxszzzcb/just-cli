import httpx
import os
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import urlparse

from just.utils.progress import progress_bar
import just.utils.echo_utils as echo


# Custom Exception Classes
class DownloadError(Exception):
    """Base exception for download errors."""
    pass


class NetworkError(DownloadError):
    """Raised when network-related errors occur during download."""
    pass


class FileSystemError(DownloadError):
    """Raised when file system operations fail during download."""
    pass


class InvalidResponseError(DownloadError):
    """Raised when server response is invalid or unexpected."""
    pass


class FileSizeMismatchError(DownloadError):
    """Raised when local file size doesn't match expected size."""
    pass


class DownloadCancelledError(DownloadError):
    """Raised when user cancels the download."""
    pass


def _download_formatter(completed, total, _elapsed, _unit, speed=None, _eta=None, _percentage=None):
    """Formatter function for download progress with file sizes and speed."""

    def format_size(size_bytes):
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(size_bytes)
        while size >= 1024.0 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
        if i == 0:
            return f"{int(size)} {size_names[i]}"
        else:
            return f"{size:.1f} {size_names[i]}"

    def format_speed(speed_bps):
        return format_size(speed_bps) + "/s"

    completed_formatted = format_size(completed)
    total_formatted = format_size(total)

    if speed is not None and speed > 0:
        speed_text = format_speed(speed)
        return f"{completed_formatted}/{total_formatted} • {speed_text}"
    else:
        return f"{completed_formatted}/{total_formatted}"


def _is_compressed_response(headers: Dict[str, str]) -> bool:
    """
    Check if response is compressed.
    
    Args:
        headers: Response headers
        
    Returns:
        True if response is compressed, False otherwise
    """
    encoding = headers.get('content-encoding', '').lower()
    return encoding in ['gzip', 'br', 'deflate', 'compress']


def _get_total_file_size(url: str, headers: Dict[str, str], verbose: bool = False) -> int:
    """
    Get the total file size by making HEAD request and fallback to range request if needed.

    Args:
        url: URL to check
        headers: Custom headers
        verbose: Enable verbose logging

    Returns:
        Total file size in bytes, or 0 if unable to determine
        
    Raises:
        NetworkError: If network request fails
    """
    try:
        if verbose:
            echo.info(f"Making HEAD request to check total file size")
        head_response = httpx.head(url, headers=headers, follow_redirects=True, timeout=30.0)
        total_size = int(head_response.headers.get('content-length', 0))
        if verbose:
            echo.info(f"HEAD response status: {head_response.status_code}")
            echo.info(f"Total size from HEAD: {total_size}")

        # If HEAD request doesn't return content-length, try a GET request with range=0-0
        if total_size == 0:
            if verbose:
                echo.info(f"HEAD request didn't return content-length, trying range request")
            range_response = httpx.get(
                url,
                headers={**headers, 'Range': 'bytes=0-0'},
                follow_redirects=True,
                timeout=30.0
            )
            total_size = _extract_total_size_from_range_response(range_response, verbose)

        return total_size
    except httpx.RequestError as e:
        raise NetworkError(f"Failed to get total file size due to network error: {e}") from e
    except (ValueError, KeyError) as e:
        if verbose:
            echo.info(f"Failed to parse content-length: {e}")
        return 0


def _extract_total_size_from_range_response(response: httpx.Response, verbose: bool = False) -> int:
    """
    Extract total file size from a range request response.

    Args:
        response: HTTP response from range request
        verbose: Enable verbose logging

    Returns:
        Total file size in bytes, or 0 if unable to determine
    """
    if 'content-range' not in response.headers:
        return 0

    content_range = response.headers.get('content-range', '')
    if not content_range.startswith('bytes '):
        return 0

    range_info = content_range[6:]  # Remove 'bytes ' prefix
    if '/' not in range_info:
        return 0

    _, total_size_str = range_info.split('/')
    if not total_size_str.isdigit():
        return 0

    total_size = int(total_size_str)
    if verbose:
        echo.info(f"Total size from range request: {total_size}")

    return total_size


def download_with_resume(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    output_file: Optional[str] = None,
    chunk_size: int = 65536,
    verbose: bool = False
) -> bool:
    """
    Download file with resume support and unified progress bar.

    Args:
        url: URL to download (required)
        headers: Custom headers (optional, defaults to empty dict)
        output_file: Output file path (optional, extracted from URL if not provided)
        chunk_size: Chunk size for downloading (default: 65536)
        verbose: Enable verbose logging (default: False)
        
    Raises:
        NetworkError: When network-related errors occur
        FileSystemError: When file system operations fail
        InvalidResponseError: When server response is invalid
        DownloadCancelledError: When user cancels the download
        DownloadError: For other unexpected errors
    """
    if headers is None:
        headers = {}
    
    if output_file is None:
        parsed_url = urlparse(url)
        output_file = os.path.basename(parsed_url.path)
        if not output_file:
            output_file = "downloaded_file"
    
    output_path = Path(output_file)
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise FileSystemError(f"Failed to create output directory: {e}") from e
    
    if verbose:
        echo.info(f"Starting download: {url}")
        echo.info(f"Output file: {output_file}")
        echo.info(f"Chunk size: {chunk_size}")

    # Use a temporary file name during download to avoid conflicts
    temp_file = output_file + ".tmp"

    # Check if final file already exists and is complete
    if os.path.exists(output_file):
        existing_file_size = os.path.getsize(output_file)
        if verbose:
            echo.info(f"Final file exists with size: {existing_file_size} bytes")

        # Get the total file size
        total_size = _get_total_file_size(url, headers, verbose)

        if existing_file_size == total_size and total_size > 0:
            echo.info(f"File already exists and is complete: {output_file}")
            return True
        else:
            # Final file exists but incomplete/corrupted, remove it
            if verbose:
                echo.info(f"Final file is incomplete or corrupted, removing it")
            try:
                os.remove(output_file)
            except OSError as e:
                raise FileSystemError(f"Failed to remove incomplete file: {e}") from e

    # Check if temporary file exists for resuming
    if os.path.exists(temp_file):
        first_byte = os.path.getsize(temp_file)
        if verbose:
            echo.info(f"Found temporary file: {first_byte} bytes")

        # Check if server returns compressed data by testing with a small range request
        try:
            if verbose:
                echo.info(f"Testing if server returns compressed data")
            test_response = httpx.get(
                url,
                headers={**headers, 'Range': 'bytes=0-0'},
                follow_redirects=True,
                timeout=30.0
            )
            
            is_compressed = _is_compressed_response(test_response.headers)
            
            if verbose:
                encoding = test_response.headers.get('content-encoding', 'none')
                echo.info(f"Server content-encoding: {encoding}, is_compressed: {is_compressed}")
            
            if is_compressed:
                echo.info(
                    f"Server returns compressed data (faster download). "
                    f"Removing temporary file to start fresh download."
                )
                try:
                    os.remove(temp_file)
                except OSError as e:
                    raise FileSystemError(f"Failed to delete temporary file: {e}") from e
                first_byte = 0
                mode = "wb"
                total_size = 0
                if verbose:
                    echo.info(f"Starting fresh download with compression")
            else:
                # Server returns uncompressed data, can safely resume
                # Get the total file size
                total_size = _get_total_file_size(url, headers, verbose)

                # Check if temporary file is larger than or equal to remote file
                if first_byte >= total_size > 0:
                    from just.utils.user_interaction import confirm_action
                    if confirm_action(f"Temporary file ({first_byte} bytes) is larger than or equal to remote file ({total_size} bytes). Delete and re-download?"):
                        try:
                            os.remove(temp_file)
                        except OSError as e:
                            raise FileSystemError(f"Failed to delete temporary file: {e}") from e
                        first_byte = 0
                        mode = "wb"
                    else:
                        raise DownloadCancelledError("Download cancelled by user")
                else:
                    # Resume download from temporary file
                    mode = "ab"
                    echo.info(f"Server returns uncompressed data. Resuming from byte {first_byte}")
                    if verbose:
                        echo.info(f"Resuming download from byte {first_byte}")
                        
        except httpx.RequestError as e:
            if verbose:
                echo.info(f"Failed to test compression, assuming fresh download: {e}")
            # If we can't test, start fresh to be safe
            try:
                os.remove(temp_file)
            except OSError:
                pass
            first_byte = 0
            mode = "wb"
            total_size = 0
    else:
        # Fresh download
        first_byte = 0
        mode = "wb"
        total_size = 0  # Will be determined later
        if verbose:
            echo.info(f"Starting fresh download")

    # Prepare headers for initial request
    request_headers = headers.copy()

    # Add Range header if resuming and first_byte is valid
    if first_byte > 0:
        # Validate that first_byte is less than total_size to avoid 416 errors
        # Ensure total_size is defined (it should be from earlier in the function, but let's be safe)
        if 'total_size' not in locals():
            total_size = 0

        if total_size > 0 and first_byte < total_size:
            request_headers['Range'] = f'bytes={first_byte}-'
            if verbose:
                echo.info(f"Added Range header: {request_headers['Range']}")
        elif first_byte >= total_size > 0:
            # If first_byte is >= total_size, start a fresh download
            first_byte = 0
            mode = "wb"
            if verbose:
                echo.info(f"First byte ({first_byte}) >= total size ({total_size}), starting fresh download")
        else:
            # If we can't determine total size, proceed with caution
            request_headers['Range'] = f'bytes={first_byte}-'
            if verbose:
                echo.info(f"Proceeding with Range header (unable to validate): {request_headers['Range']}")

    try:
        if verbose:
            echo.info(
                f"Making initial request with headers: "
                f"{request_headers}"
            )

        with httpx.stream("GET", url, headers=request_headers, follow_redirects=True, timeout=30.0) as response:
            if verbose:
                echo.info(
                    f"Initial response status: {response.status_code}"
                )
                echo.info(
                    f"Response headers: {dict(response.headers)}"
                )

            response.raise_for_status()

            # Check if server supports range requests
            if first_byte > 0 and response.status_code != 206:
                return _handle_server_no_range_support(
                    url, headers, output_file, chunk_size,
                    verbose, response
                )

            # Server supports range requests or it's a fresh download
            total_size = _get_total_size(response, first_byte, verbose)

            # Validate total size
            if total_size is None:
                raise InvalidResponseError(f"Invalid server response: HTTP {response.status_code}")

            # Download file with resume support to temporary file
            success = _download_stream(response, temp_file, total_size, mode, first_byte, chunk_size, verbose)

            # If download is successful, rename temporary file to final name
            if success:
                try:
                    os.rename(temp_file, output_file)
                    if verbose:
                        echo.info(f"Download completed and renamed to: {output_file}")
                except OSError as e:
                    raise FileSystemError(f"Failed to finalize downloaded file: {e}") from e

            return success

    except httpx.HTTPStatusError as e:
        raise NetworkError(f"HTTP error occurred: {e.response.status_code} {e.response.reason_phrase}") from e
    except httpx.RequestError as e:
        raise NetworkError(f"Network error occurred: {e}") from e
    except (DownloadError, FileSystemError, NetworkError, InvalidResponseError, DownloadCancelledError):
        # Re-raise our custom exceptions
        # Clean up temporary file on failure
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
                if verbose:
                    echo.info(f"Cleaned up temporary file: {temp_file}")
            except OSError:
                pass
        raise
    except Exception as e:
        # Wrap unexpected exceptions
        # Clean up temporary file on failure
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
                if verbose:
                    echo.info(f"Cleaned up temporary file: {temp_file}")
            except OSError:
                pass
        raise DownloadError(f"Unexpected error during download: {e}") from e


def _handle_server_no_range_support(
    url: str,
    headers: Dict[str, str],
    output_file: str,
    chunk_size: int,
    verbose: bool,
    response: httpx.Response
) -> bool:
    """Handle case where server doesn't support range requests."""
    if verbose:
        echo.info(
            f"Server doesn't support range requests "
            f"(status: {response.status_code}), restarting download"
        )

    # Server doesn't support range requests, start from beginning
    first_byte = 0
    mode = "wb"

    # Close the current stream and make a new request
    response.close()

    if verbose:
        echo.info(f"Making fresh request without Range header")

    # Make a new request without the Range header
    with httpx.stream("GET", url, headers=headers, follow_redirects=True, timeout=30.0) as new_response:
        if verbose:
            echo.info(f"Fresh response status: {new_response.status_code}")

        new_response.raise_for_status()

        # Get total file size for fresh download
        total_size = int(new_response.headers.get('content-length', 0))
        if verbose:
            echo.info(f"Fresh download total size: {total_size}")

        # Download file with fresh start to temporary file
        temp_file = output_file + ".tmp"
        success = _download_stream(
            new_response,
            temp_file,
            total_size,
            mode,
            first_byte,
            chunk_size,
            verbose
        )

        # If download is successful, rename temporary file to final name
        if success:
            try:
                os.rename(temp_file, output_file)
                if verbose:
                    echo.info(f"Download completed and renamed to: {output_file}")
            except OSError as e:
                raise FileSystemError(f"Failed to finalize downloaded file: {e}") from e

        return success


def _get_total_size(response: httpx.Response, first_byte: int, verbose: bool) -> Optional[int]:
    """Get total file size from response."""
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
        if verbose:
            echo.info(
                f"Partial content (206), content-range: "
                f"{content_range}, total size: {total_size}"
            )
    elif response.status_code == 200:
        # Full content
        total_size = int(response.headers.get('content-length', 0))
        if verbose:
            echo.info(
                f"Full content (200), total size: {total_size}"
            )
    else:
        return None

    return total_size


def _download_stream(
    response: httpx.Response,
    output_file: str,
    total_size: int,
    mode: str,
    first_byte: int,
    chunk_size: int = 65536,
    verbose: bool = False
) -> bool:
    """
    Helper function to download file stream.

    Args:
        response: HTTP response stream
        output_file: Output file path (can be temporary file)
        total_size: Total file size
        mode: File open mode ("wb" or "ab")
        first_byte: Starting byte position
        chunk_size: Chunk size for downloading
        verbose: Enable verbose logging
        
    Raises:
        FileSystemError: When file write operations fail
        DownloadError: When download fails
    """
    if verbose:
        echo.info(
            f"Starting _download_stream: total_size={total_size}, "
            f"mode={mode}, first_byte={first_byte}"
        )

    # Download file with unified progress bar
    bytes_written = 0

    if verbose:
        echo.info(
            f"Opening file {output_file} with mode {mode}"
        )

    # Prepare progress bar arguments with both columns and formatter
    # Rich mode will prefer columns, Simple mode will use formatter
    from rich.progress import FileSizeColumn, TransferSpeedColumn, TextColumn
    download_columns = [
        FileSizeColumn(),  # Shows completed/total file size with proper units
        TextColumn("•"),
        TransferSpeedColumn()  # Shows download speed
    ]

    # Ensure total_size is valid (non-negative) before passing to progress bar
    # If total_size is negative, set it to 0 to avoid "total must be greater than or equal to 0" error
    validated_total_size = max(0, total_size)
    
    progress_kwargs = {
        "total": validated_total_size,
        "desc": "Downloading",
        "unit": "b",
        "progress_desc_columns": download_columns,
        "progress_desc_formatter": _download_formatter
    }

    try:
        with open(output_file, mode) as f:
            with progress_bar(**progress_kwargs) as pbar:
                # Update progress for already downloaded bytes
                pbar.n = first_byte
                pbar.refresh()  # Force refresh to show correct initial position
                if verbose:
                    echo.info(
                        f"Progress bar initialized with n={first_byte}"
                    )

                for i, chunk in enumerate(response.iter_bytes(chunk_size=chunk_size)):
                    if chunk:
                        f.write(chunk)
                        bytes_written += len(chunk)
                        pbar.update(len(chunk))

                        if verbose and (i % 10 == 0 or len(chunk) < chunk_size):
                            # Log every 10 chunks or last chunk
                            echo.info(
                                f"Chunk {i}: wrote {len(chunk)} bytes, "
                                f"total written: {bytes_written}"
                            )
    except OSError as e:
        raise FileSystemError(f"Failed to write to file {output_file}: {e}") from e
    except Exception as e:
        raise DownloadError(f"Error during file download: {e}") from e

    if verbose:
        echo.info(
            f"Download completed: {output_file}, "
            f"total bytes written: {bytes_written}"
        )

    echo.info(f"Download completed: {output_file}")
    return True