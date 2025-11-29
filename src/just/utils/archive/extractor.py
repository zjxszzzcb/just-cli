from pathlib import Path
from typing import Optional

import just.utils.echo_utils as echo
from .format_detect import ArchiveFormat, detect_archive_format
from .zip_handler import extract_zip
from .tar_handler import extract_tar
from .compression_handler import extract_gzip, extract_bzip2, extract_xz, extract_zstd
from .sevenzip_handler import extract_7z


def extract(archive_path: str, output_dir: Optional[str] = None) -> bool:
    """
    Universal archive extraction interface.
    
    Automatically detects archive format using magic bytes and file extension,
    then extracts using the appropriate handler.
    
    Supported formats:
    - ZIP (.zip)
    - TAR (.tar, .tar.gz, .tgz, .tar.bz2, .tbz, .tar.xz, .txz, .tar.zst, .tzst)
    - GZIP (.gz)
    - BZIP2 (.bz2)
    - XZ/LZMA (.xz)
    - ZSTD (.zst)
    - 7Z (.7z) - requires py7zr package
    
    Note: RAR requires rarfile package which is not included by default.
    
    Args:
        archive_path: Path to the archive file
        output_dir: Directory to extract to. If None, uses format-specific defaults
        
    Returns:
        True if successful, False otherwise
        
    Examples:
        >>> extract("archive.zip")
        >>> extract("archive.tar.gz", "/tmp/output")
        >>> extract("data.xz", "extracted/")
    """
    if not Path(archive_path).exists():
        echo.error(f"Archive not found: {archive_path}")
        return False
    
    fmt = detect_archive_format(archive_path)
    
    if fmt == ArchiveFormat.ZIP:
        return extract_zip(archive_path, output_dir)
    
    elif fmt == ArchiveFormat.TAR:
        return extract_tar(archive_path, output_dir, compression=None)
    
    elif fmt == ArchiveFormat.TAR_GZ:
        return extract_tar(archive_path, output_dir, compression='gz')
    
    elif fmt == ArchiveFormat.TAR_BZ2:
        return extract_tar(archive_path, output_dir, compression='bz2')
    
    elif fmt == ArchiveFormat.TAR_XZ:
        return extract_tar(archive_path, output_dir, compression='xz')
    
    elif fmt == ArchiveFormat.TAR_ZST:
        return extract_tar(archive_path, output_dir, compression='zst')
    
    elif fmt == ArchiveFormat.GZIP:
        return extract_gzip(archive_path, output_dir)
    
    elif fmt == ArchiveFormat.BZIP2:
        return extract_bzip2(archive_path, output_dir)
    
    elif fmt == ArchiveFormat.XZ:
        return extract_xz(archive_path, output_dir)
    
    elif fmt == ArchiveFormat.ZSTD:
        return extract_zstd(archive_path, output_dir)
    
    elif fmt == ArchiveFormat.SEVEN_ZIP:
        return extract_7z(archive_path, output_dir)
    
    elif fmt == ArchiveFormat.RAR:
        echo.error("RAR format detected but not supported. Install rarfile: pip install rarfile")
        return False
    
    else:
        echo.error(f"Unknown or unsupported archive format: {archive_path}")
        return False
