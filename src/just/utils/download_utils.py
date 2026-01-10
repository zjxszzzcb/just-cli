"""
Download Utilities
==================

Provides file download with resume support and progress display.
"""

import httpx
import os
from pathlib import Path
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse
from dataclasses import dataclass

from just.utils.progress import progress_bar
import just.utils.echo_utils as echo


# =============================================================================
# Exceptions
# =============================================================================

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


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class DownloadState:
    """Holds the state for a download operation."""
    first_byte: int = 0
    mode: str = "wb"
    total_size: int = 0


# =============================================================================
# Helper Functions
# =============================================================================

def _format_size(size_bytes: int) -> str:
    """Format bytes to human readable string."""
    if size_bytes == 0:
        return "0 B"
    
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(size_bytes)
    unit_index = 0
    
    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    return f"{size:.1f} {units[unit_index]}"


def _download_formatter(completed, total, _elapsed, _unit, speed=None, _eta=None, _percentage=None):
    """Formatter for download progress bar."""
    completed_str = _format_size(completed)
    total_str = _format_size(total)
    
    if speed and speed > 0:
        return f"{completed_str}/{total_str} • {_format_size(speed)}/s"
    return f"{completed_str}/{total_str}"


def _is_compressed(headers: Dict[str, str]) -> bool:
    """Check if response is compressed."""
    encoding = headers.get('content-encoding', '').lower()
    return encoding in ['gzip', 'br', 'deflate', 'compress']


def _safe_remove(path: str) -> None:
    """Remove file if exists, ignore errors."""
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


def _remove_file(path: str, error_msg: str) -> None:
    """Remove file or raise FileSystemError."""
    try:
        os.remove(path)
    except OSError as e:
        raise FileSystemError(f"{error_msg}: {e}") from e


# =============================================================================
# Size Detection
# =============================================================================

def _get_size_from_head(url: str, headers: Dict[str, str], verbose: bool) -> int:
    """Get file size from HEAD request."""
    if verbose:
        echo.info("Making HEAD request to check total file size")
    
    response = httpx.head(url, headers=headers, follow_redirects=True, timeout=30.0)
    size = int(response.headers.get('content-length', 0))
    
    if verbose:
        echo.info(f"HEAD response: {response.status_code}, size: {size}")
    
    return size


def _get_size_from_range(url: str, headers: Dict[str, str], verbose: bool) -> int:
    """Get file size from range request (bytes 0-0)."""
    if verbose:
        echo.info("Trying range request for size")
    
    response = httpx.get(
        url,
        headers={**headers, 'Range': 'bytes=0-0'},
        follow_redirects=True,
        timeout=30.0
    )
    
    content_range = response.headers.get('content-range', '')
    if not content_range.startswith('bytes '):
        return 0
    
    # Format: "bytes 0-0/12345"
    range_info = content_range[6:]
    if '/' not in range_info:
        return 0
    
    total_str = range_info.split('/')[1]
    if not total_str.isdigit():
        return 0
    
    size = int(total_str)
    if verbose:
        echo.info(f"Size from range request: {size}")
    
    return size


def _get_total_file_size(url: str, headers: Dict[str, str], verbose: bool = False) -> int:
    """Get total file size, trying HEAD first then range request."""
    try:
        size = _get_size_from_head(url, headers, verbose)
        if size > 0:
            return size
        return _get_size_from_range(url, headers, verbose)
    except httpx.RequestError as e:
        raise NetworkError(f"Failed to get file size: {e}") from e
    except (ValueError, KeyError) as e:
        if verbose:
            echo.info(f"Failed to parse content-length: {e}")
        return 0


def _parse_content_range(response: httpx.Response) -> int:
    """Parse total size from content-range header."""
    content_range = response.headers.get('content-range', '')
    if not content_range.startswith('bytes '):
        return 0
    
    range_info = content_range[6:]
    if '/' not in range_info:
        return 0
    
    total_str = range_info.split('/')[1]
    return int(total_str) if total_str.isdigit() else 0


# =============================================================================
# Resume Logic
# =============================================================================

def _check_existing_complete(output_file: str, url: str, headers: Dict[str, str], verbose: bool) -> bool:
    """Check if file already exists and is complete. Returns True if complete."""
    if not os.path.exists(output_file):
        return False
    
    existing_size = os.path.getsize(output_file)
    if verbose:
        echo.info(f"Final file exists: {existing_size} bytes")
    
    total_size = _get_total_file_size(url, headers, verbose)
    
    if existing_size == total_size and total_size > 0:
        echo.info(f"File already complete: {output_file}")
        return True
    
    # Incomplete/corrupted, remove it
    if verbose:
        echo.info("File incomplete, removing")
    _remove_file(output_file, "Failed to remove incomplete file")
    return False


def _handle_temp_file(
    temp_file: str,
    url: str,
    headers: Dict[str, str],
    verbose: bool,
    auto_confirm: bool
) -> DownloadState:
    """Handle existing temp file. Returns DownloadState for next steps."""
    if not os.path.exists(temp_file):
        if verbose:
            echo.info("Starting fresh download")
        return DownloadState(first_byte=0, mode="wb", total_size=0)
    
    first_byte = os.path.getsize(temp_file)
    if verbose:
        echo.info(f"Found temp file: {first_byte} bytes")
    
    # Test if server returns compressed data
    try:
        return _check_compression_and_resume(temp_file, url, headers, first_byte, verbose, auto_confirm)
    except httpx.RequestError as e:
        if verbose:
            echo.info(f"Compression test failed, starting fresh: {e}")
        _safe_remove(temp_file)
        return DownloadState(first_byte=0, mode="wb", total_size=0)


def _check_compression_and_resume(
    temp_file: str,
    url: str,
    headers: Dict[str, str],
    first_byte: int,
    verbose: bool,
    auto_confirm: bool
) -> DownloadState:
    """Check compression and decide resume strategy."""
    if verbose:
        echo.info("Testing server compression")
    
    response = httpx.get(
        url,
        headers={**headers, 'Range': 'bytes=0-0'},
        follow_redirects=True,
        timeout=30.0
    )
    
    if _is_compressed(response.headers):
        # Compressed = can't resume, start fresh
        echo.info("Server returns compressed data, starting fresh download")
        _remove_file(temp_file, "Failed to delete temp file")
        return DownloadState(first_byte=0, mode="wb", total_size=0)
    
    # Uncompressed = can resume
    if verbose:
        encoding = response.headers.get('content-encoding', 'none')
        echo.info(f"Content-encoding: {encoding}")
    
    total_size = _get_total_file_size(url, headers, verbose)
    
    # Temp file too large?
    if first_byte >= total_size > 0:
        return _handle_oversized_temp(temp_file, first_byte, total_size, auto_confirm)
    
    echo.info(f"Resuming from byte {first_byte}")
    return DownloadState(first_byte=first_byte, mode="ab", total_size=total_size)


def _handle_oversized_temp(
    temp_file: str,
    first_byte: int,
    total_size: int,
    auto_confirm: bool
) -> DownloadState:
    """Handle temp file that's larger than remote file."""
    should_delete = auto_confirm
    
    if not auto_confirm:
        from just.utils.user_interaction import confirm_action
        msg = f"Temp file ({first_byte}B) >= remote ({total_size}B). Delete and re-download?"
        should_delete = confirm_action(msg)
    
    if not should_delete:
        raise DownloadCancelledError("Download cancelled by user")
    
    _remove_file(temp_file, "Failed to delete temp file")
    return DownloadState(first_byte=0, mode="wb", total_size=0)


# =============================================================================
# Download Execution
# =============================================================================

def _prepare_request_headers(
    headers: Dict[str, str],
    state: DownloadState,
    verbose: bool
) -> Dict[str, str]:
    """Prepare request headers, adding Range if resuming."""
    request_headers = headers.copy()
    
    if state.first_byte <= 0:
        return request_headers
    
    # Add Range header for resume
    if state.total_size > 0 and state.first_byte >= state.total_size:
        # Should not happen, but handle gracefully
        if verbose:
            echo.info("first_byte >= total_size, starting fresh")
        state.first_byte = 0
        state.mode = "wb"
        return request_headers
    
    request_headers['Range'] = f'bytes={state.first_byte}-'
    if verbose:
        echo.info(f"Range header: {request_headers['Range']}")
    
    return request_headers


def _get_response_total_size(response: httpx.Response, first_byte: int, verbose: bool) -> Optional[int]:
    """Extract total size from response."""
    if response.status_code == 206:
        total = _parse_content_range(response)
        if verbose:
            echo.info(f"Partial content (206), total: {total}")
        return total if total > 0 else first_byte
    
    if response.status_code == 200:
        total = int(response.headers.get('content-length', 0))
        if verbose:
            echo.info(f"Full content (200), total: {total}")
        return total
    
    return None


def _download_stream(
    response: httpx.Response,
    output_file: str,
    total_size: int,
    mode: str,
    first_byte: int,
    chunk_size: int = 65536,
    verbose: bool = False
) -> bool:
    """Download response stream to file with progress bar."""
    if verbose:
        echo.info(f"Downloading: total={total_size}, mode={mode}, offset={first_byte}")
    
    from rich.progress import FileSizeColumn, TransferSpeedColumn, TextColumn
    
    progress_kwargs = {
        "total": max(0, total_size),
        "desc": "Downloading",
        "unit": "b",
        "progress_desc_columns": [FileSizeColumn(), TextColumn("•"), TransferSpeedColumn()],
        "progress_desc_formatter": _download_formatter
    }
    
    bytes_written = 0
    
    try:
        with open(output_file, mode) as f, progress_bar(**progress_kwargs) as pbar:
            pbar.n = first_byte
            pbar.refresh()
            
            for i, chunk in enumerate(response.iter_bytes(chunk_size=chunk_size)):
                if not chunk:
                    continue
                f.write(chunk)
                bytes_written += len(chunk)
                pbar.update(len(chunk))
                
                if verbose and (i % 10 == 0 or len(chunk) < chunk_size):
                    echo.info(f"Chunk {i}: {len(chunk)}B, total: {bytes_written}B")
    
    except OSError as e:
        raise FileSystemError(f"Write failed: {e}") from e
    
    if verbose:
        echo.info(f"Download completed: {bytes_written} bytes")
    
    echo.info(f"Download completed: {output_file}")
    return True


def _finalize_download(temp_file: str, output_file: str, verbose: bool) -> None:
    """Rename temp file to final output file."""
    try:
        os.rename(temp_file, output_file)
        if verbose:
            echo.info(f"Renamed to: {output_file}")
    except OSError as e:
        raise FileSystemError(f"Failed to finalize: {e}") from e


def _download_fresh(
    url: str,
    headers: Dict[str, str],
    temp_file: str,
    output_file: str,
    chunk_size: int,
    verbose: bool,
    response: httpx.Response
) -> bool:
    """Handle fresh download when server doesn't support Range."""
    if verbose:
        echo.info(f"Server doesn't support Range, starting fresh")
    
    response.close()
    
    with httpx.stream("GET", url, headers=headers, follow_redirects=True, timeout=30.0) as r:
        r.raise_for_status()
        total = int(r.headers.get('content-length', 0))
        
        success = _download_stream(r, temp_file, total, "wb", 0, chunk_size, verbose)
        if success:
            _finalize_download(temp_file, output_file, verbose)
        return success


# =============================================================================
# Main Entry Point
# =============================================================================

def download_with_resume(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    output_file: Optional[str] = None,
    chunk_size: int = 65536,
    verbose: bool = False,
    auto_confirm: bool = False
) -> bool:
    """
    Download file with resume support.

    Args:
        url: URL to download
        headers: Custom headers
        output_file: Output path (extracted from URL if not provided)
        chunk_size: Download chunk size
        verbose: Enable verbose logging
        auto_confirm: Skip confirmation prompts

    Raises:
        NetworkError: Network failures
        FileSystemError: File operation failures
        InvalidResponseError: Invalid server response
        DownloadCancelledError: User cancelled
    """
    headers = headers or {}
    
    # Determine output file
    if output_file is None:
        output_file = os.path.basename(urlparse(url).path) or "downloaded_file"
    
    # Create output directory
    try:
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise FileSystemError(f"Failed to create directory: {e}") from e
    
    if verbose:
        echo.info(f"Download: {url}")
        echo.info(f"Output: {output_file}")
    
    temp_file = output_file + ".tmp"
    
    # Check if already complete
    if _check_existing_complete(output_file, url, headers, verbose):
        return True
    
    # Handle temp file / resume state
    state = _handle_temp_file(temp_file, url, headers, verbose, auto_confirm)
    request_headers = _prepare_request_headers(headers, state, verbose)
    
    try:
        return _execute_download(url, request_headers, temp_file, output_file, state, chunk_size, verbose)
    except (NetworkError, FileSystemError, InvalidResponseError, DownloadCancelledError):
        _safe_remove(temp_file)
        raise
    except httpx.HTTPStatusError as e:
        _safe_remove(temp_file)
        raise NetworkError(f"HTTP {e.response.status_code}") from e
    except httpx.RequestError as e:
        _safe_remove(temp_file)
        raise NetworkError(f"Network error: {e}") from e
    except Exception as e:
        _safe_remove(temp_file)
        raise DownloadError(f"Unexpected error: {e}") from e


def _execute_download(
    url: str,
    headers: Dict[str, str],
    temp_file: str,
    output_file: str,
    state: DownloadState,
    chunk_size: int,
    verbose: bool
) -> bool:
    """Execute the actual download."""
    if verbose:
        echo.info(f"Request headers: {headers}")
    
    with httpx.stream("GET", url, headers=headers, follow_redirects=True, timeout=30.0) as response:
        if verbose:
            echo.info(f"Response: {response.status_code}")
        
        response.raise_for_status()
        
        # Server doesn't support Range?
        if state.first_byte > 0 and response.status_code != 206:
            return _download_fresh(url, headers, temp_file, output_file, chunk_size, verbose, response)
        
        # Get total size
        total = _get_response_total_size(response, state.first_byte, verbose)
        if total is None:
            raise InvalidResponseError(f"Invalid response: HTTP {response.status_code}")
        
        # Download
        success = _download_stream(response, temp_file, total, state.mode, state.first_byte, chunk_size, verbose)
        
        if success:
            _finalize_download(temp_file, output_file, verbose)
        
        return success