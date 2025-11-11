from enum import Enum
from pathlib import Path
from typing import Optional


class ArchiveFormat(Enum):
    """Supported archive formats."""
    ZIP = "zip"
    TAR = "tar"
    TAR_GZ = "tar.gz"
    TAR_BZ2 = "tar.bz2"
    TAR_XZ = "tar.xz"
    TAR_ZST = "tar.zst"
    GZIP = "gzip"
    BZIP2 = "bzip2"
    XZ = "xz"
    ZSTD = "zstd"
    SEVEN_ZIP = "7z"
    RAR = "rar"
    UNKNOWN = "unknown"


MAGIC_BYTES = {
    ArchiveFormat.ZIP: [
        b'\x50\x4B\x03\x04',
        b'\x50\x4B\x05\x06',
        b'\x50\x4B\x07\x08',
    ],
    ArchiveFormat.GZIP: [
        b'\x1F\x8B\x08',
    ],
    ArchiveFormat.BZIP2: [
        b'\x42\x5A\x68',
    ],
    ArchiveFormat.XZ: [
        b'\xFD\x37\x7A\x58\x5A\x00',
    ],
    ArchiveFormat.ZSTD: [
        b'\x28\xB5\x2F\xFD',
    ],
    ArchiveFormat.SEVEN_ZIP: [
        b'\x37\x7A\xBC\xAF\x27\x1C',
    ],
    ArchiveFormat.RAR: [
        b'\x52\x61\x72\x21\x1A\x07\x00',
        b'\x52\x61\x72\x21\x1A\x07\x01\x00',
    ],
}


EXTENSION_MAP = {
    '.zip': ArchiveFormat.ZIP,
    '.tar': ArchiveFormat.TAR,
    '.tar.gz': ArchiveFormat.TAR_GZ,
    '.tgz': ArchiveFormat.TAR_GZ,
    '.tar.bz2': ArchiveFormat.TAR_BZ2,
    '.tbz': ArchiveFormat.TAR_BZ2,
    '.tbz2': ArchiveFormat.TAR_BZ2,
    '.tar.xz': ArchiveFormat.TAR_XZ,
    '.txz': ArchiveFormat.TAR_XZ,
    '.tar.zst': ArchiveFormat.TAR_ZST,
    '.tzst': ArchiveFormat.TAR_ZST,
    '.gz': ArchiveFormat.GZIP,
    '.bz2': ArchiveFormat.BZIP2,
    '.xz': ArchiveFormat.XZ,
    '.zst': ArchiveFormat.ZSTD,
    '.7z': ArchiveFormat.SEVEN_ZIP,
    '.rar': ArchiveFormat.RAR,
}


def detect_format_by_magic_bytes(file_path: str) -> Optional[ArchiveFormat]:
    """
    Detect archive format by reading magic bytes from file.
    
    Args:
        file_path: Path to the archive file
        
    Returns:
        ArchiveFormat enum or None if unknown
    """

    with open(file_path, 'rb') as f:
        header = f.read(16)

        for fmt, signatures in MAGIC_BYTES.items():
            for signature in signatures:
                if header.startswith(signature):
                    if fmt == ArchiveFormat.GZIP:
                        return detect_tar_gz_or_gzip(file_path)
                    elif fmt == ArchiveFormat.BZIP2:
                        return detect_tar_bz2_or_bzip2(file_path)
                    elif fmt == ArchiveFormat.XZ:
                        return detect_tar_xz_or_xz(file_path)
                    elif fmt == ArchiveFormat.ZSTD:
                        return detect_tar_zst_or_zstd(file_path)
                    return fmt

        if b'ustar' in header or (len(header) >= 257 and header[257:262] == b'ustar'):
            return ArchiveFormat.TAR

        f.seek(257)
        tar_magic = f.read(5)
        if tar_magic == b'ustar':
            return ArchiveFormat.TAR
    
    return None


def detect_tar_gz_or_gzip(file_path: str) -> ArchiveFormat:
    """Check if gzip file contains a tar archive."""
    import gzip

    with gzip.open(file_path, 'rb') as gz:
        header = gz.read(512)
        if b'ustar' in header:
            return ArchiveFormat.TAR_GZ

    return ArchiveFormat.GZIP


def detect_tar_bz2_or_bzip2(file_path: str) -> ArchiveFormat:
    """Check if bzip2 file contains a tar archive."""
    import bz2
    with bz2.open(file_path, 'rb') as bz:
        header = bz.read(512)
        if b'ustar' in header:
            return ArchiveFormat.TAR_BZ2
    return ArchiveFormat.BZIP2


def detect_tar_xz_or_xz(file_path: str) -> ArchiveFormat:
    """Check if xz file contains a tar archive."""
    import lzma

    with lzma.open(file_path, 'rb') as xz:
        header = xz.read(512)
        if b'ustar' in header:
            return ArchiveFormat.TAR_XZ

    return ArchiveFormat.XZ


def detect_tar_zst_or_zstd(file_path: str) -> ArchiveFormat:
    """Check if zstd file contains a tar archive."""
    import zstandard as zstd

    with open(file_path, 'rb') as f:
        dctx = zstd.ZstdDecompressor()
        with dctx.stream_reader(f) as reader:
            header = reader.read(512)
            if b'ustar' in header:
                return ArchiveFormat.TAR_ZST

    return ArchiveFormat.ZSTD


def detect_format_by_extension(file_path: str) -> Optional[ArchiveFormat]:
    """
    Detect archive format by file extension.
    
    Args:
        file_path: Path to the archive file
        
    Returns:
        ArchiveFormat enum or None if unknown
    """
    path = Path(file_path)
    name_lower = path.name.lower()
    
    for ext, fmt in sorted(EXTENSION_MAP.items(), key=lambda x: -len(x[0])):
        if name_lower.endswith(ext):
            return fmt
    
    return None


def detect_archive_format(file_path: str) -> ArchiveFormat:
    """
    Detect archive format using magic bytes first, then fallback to extension.
    
    Args:
        file_path: Path to the archive file
        
    Returns:
        ArchiveFormat enum (UNKNOWN if cannot detect)
    """
    if not Path(file_path).exists():
        return ArchiveFormat.UNKNOWN
    
    fmt = detect_format_by_magic_bytes(file_path)
    if fmt:
        return fmt
    
    fmt = detect_format_by_extension(file_path)
    if fmt:
        return fmt
    
    return ArchiveFormat.UNKNOWN
