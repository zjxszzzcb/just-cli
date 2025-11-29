import tempfile
import shutil
import gzip
import bz2
import lzma
from pathlib import Path

from just.utils.archive import (
    extract, 
    detect_archive_format, 
    ArchiveFormat,
    create_zip,
    create_tar,
)
import just.utils.echo_utils as echo


def create_test_file_structure(base_dir: Path):
    """Create test file structure for archiving."""
    test_dir = base_dir / "test_data"
    test_dir.mkdir()
    (test_dir / "file1.txt").write_text("Hello from file1")
    (test_dir / "file2.txt").write_text("Hello from file2")
    
    subdir = test_dir / "subdir"
    subdir.mkdir()
    (subdir / "file3.txt").write_text("Hello from subdir")
    
    return test_dir


def verify_extracted_files(extract_dir: Path, base_name: str = "test_data"):
    """Verify that extracted files are correct."""
    assert (extract_dir / base_name / "file1.txt").exists()
    assert (extract_dir / base_name / "file2.txt").exists()
    assert (extract_dir / base_name / "subdir" / "file3.txt").exists()
    
    content = (extract_dir / base_name / "file1.txt").read_text()
    assert content == "Hello from file1"


def test_format_detection():
    """Test archive format detection by magic bytes and extension."""
    echo.info("Testing format detection...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        test_dir = create_test_file_structure(tmpdir)
        
        echo.info("  Creating test archives...")
        create_zip(str(tmpdir / "test.zip"), [str(test_dir)], base_dir=str(tmpdir))
        create_tar(str(tmpdir / "test.tar"), [str(test_dir)], compression=None, base_dir=str(tmpdir))
        create_tar(str(tmpdir / "test.tar.gz"), [str(test_dir)], compression='gz', base_dir=str(tmpdir))
        create_tar(str(tmpdir / "test.tar.bz2"), [str(test_dir)], compression='bz2', base_dir=str(tmpdir))
        create_tar(str(tmpdir / "test.tar.xz"), [str(test_dir)], compression='xz', base_dir=str(tmpdir))
        
        with gzip.open(tmpdir / "test.txt.gz", 'wb') as f:
            f.write(b"Test gzip content")
        
        with bz2.open(tmpdir / "test.txt.bz2", 'wb') as f:
            f.write(b"Test bzip2 content")
        
        with lzma.open(tmpdir / "test.txt.xz", 'wb') as f:
            f.write(b"Test xz content")
        
        echo.info("  Testing ZIP detection...")
        fmt = detect_archive_format(str(tmpdir / "test.zip"))
        assert fmt == ArchiveFormat.ZIP, f"Expected ZIP, got {fmt}"
        
        echo.info("  Testing TAR detection...")
        fmt = detect_archive_format(str(tmpdir / "test.tar"))
        assert fmt == ArchiveFormat.TAR, f"Expected TAR, got {fmt}"
        
        echo.info("  Testing TAR.GZ detection...")
        fmt = detect_archive_format(str(tmpdir / "test.tar.gz"))
        assert fmt == ArchiveFormat.TAR_GZ, f"Expected TAR_GZ, got {fmt}"
        
        echo.info("  Testing TAR.BZ2 detection...")
        fmt = detect_archive_format(str(tmpdir / "test.tar.bz2"))
        assert fmt == ArchiveFormat.TAR_BZ2, f"Expected TAR_BZ2, got {fmt}"
        
        echo.info("  Testing TAR.XZ detection...")
        fmt = detect_archive_format(str(tmpdir / "test.tar.xz"))
        assert fmt == ArchiveFormat.TAR_XZ, f"Expected TAR_XZ, got {fmt}"
        
        echo.info("  Testing GZIP detection...")
        fmt = detect_archive_format(str(tmpdir / "test.txt.gz"))
        assert fmt == ArchiveFormat.GZIP, f"Expected GZIP, got {fmt}"
        
        echo.info("  Testing BZIP2 detection...")
        fmt = detect_archive_format(str(tmpdir / "test.txt.bz2"))
        assert fmt == ArchiveFormat.BZIP2, f"Expected BZIP2, got {fmt}"
        
        echo.info("  Testing XZ detection...")
        fmt = detect_archive_format(str(tmpdir / "test.txt.xz"))
        assert fmt == ArchiveFormat.XZ, f"Expected XZ, got {fmt}"
        
        try:
            import zstandard
            create_tar(str(tmpdir / "test.tar.zst"), [str(test_dir)], compression='zst', base_dir=str(tmpdir))
            
            with open(tmpdir / "test.txt.zst", 'wb') as f:
                cctx = zstandard.ZstdCompressor()
                f.write(cctx.compress(b"Test zstd content"))
            
            echo.info("  Testing TAR.ZST detection...")
            fmt = detect_archive_format(str(tmpdir / "test.tar.zst"))
            assert fmt == ArchiveFormat.TAR_ZST, f"Expected TAR_ZST, got {fmt}"
            
            echo.info("  Testing ZSTD detection...")
            fmt = detect_archive_format(str(tmpdir / "test.txt.zst"))
            assert fmt == ArchiveFormat.ZSTD, f"Expected ZSTD, got {fmt}"
        except ImportError:
            echo.warning("  zstandard not available, skipping ZSTD tests")
    
    echo.info("Format detection tests passed!")


def test_zip_extraction():
    """Test ZIP archive extraction."""
    echo.info("\nTesting ZIP extraction...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        test_dir = create_test_file_structure(tmpdir)
        archive_path = tmpdir / "test.zip"
        create_zip(str(archive_path), [str(test_dir)], base_dir=str(tmpdir))
        
        extract_dir = tmpdir / "extracted"
        success = extract(str(archive_path), str(extract_dir))
        assert success, "ZIP extraction failed"
        
        verify_extracted_files(extract_dir)
    
    echo.info("ZIP extraction test passed!")


def test_tar_formats_extraction():
    """Test TAR archive extraction with various compressions."""
    echo.info("\nTesting TAR format extractions...")
    
    formats = [
        ('test.tar', None, ArchiveFormat.TAR),
        ('test.tar.gz', 'gz', ArchiveFormat.TAR_GZ),
        ('test.tgz', 'gz', ArchiveFormat.TAR_GZ),
        ('test.tar.bz2', 'bz2', ArchiveFormat.TAR_BZ2),
        ('test.tar.xz', 'xz', ArchiveFormat.TAR_XZ),
    ]
    
    try:
        import zstandard
        formats.append(('test.tar.zst', 'zst', ArchiveFormat.TAR_ZST))
        echo.info("  zstandard available, will test .tar.zst")
    except ImportError:
        echo.warning("  zstandard not available, skipping .tar.zst")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        test_dir = create_test_file_structure(tmpdir)
        
        for archive_name, compression, expected_fmt in formats:
            echo.info(f"  Testing {archive_name}...")
            
            archive_path = tmpdir / archive_name
            create_tar(str(archive_path), [str(test_dir)], compression=compression, base_dir=str(tmpdir))
            
            fmt = detect_archive_format(str(archive_path))
            assert fmt == expected_fmt, f"Expected {expected_fmt}, got {fmt}"
            
            extract_dir = tmpdir / f"extracted_{archive_name}"
            success = extract(str(archive_path), str(extract_dir))
            assert success, f"Extraction of {archive_name} failed"
            
            verify_extracted_files(extract_dir)
            echo.info(f"    {archive_name} passed!")
    
    echo.info("TAR format extraction tests passed!")


def test_compression_formats():
    """Test standalone compression format extraction (gzip, bzip2, xz, zstd)."""
    echo.info("\nTesting compression format extractions...")
    
    test_content = b"This is test content for compression formats"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        echo.info("  Testing GZIP...")
        gz_path = tmpdir / "test.txt.gz"
        with gzip.open(gz_path, 'wb') as f:
            f.write(test_content)
        
        fmt = detect_archive_format(str(gz_path))
        assert fmt == ArchiveFormat.GZIP
        
        extract_dir = tmpdir / "extracted_gz"
        success = extract(str(gz_path), str(extract_dir))
        assert success
        assert (extract_dir / "test.txt").read_bytes() == test_content
        
        echo.info("  Testing BZIP2...")
        bz2_path = tmpdir / "test.txt.bz2"
        with bz2.open(bz2_path, 'wb') as f:
            f.write(test_content)
        
        fmt = detect_archive_format(str(bz2_path))
        assert fmt == ArchiveFormat.BZIP2
        
        extract_dir = tmpdir / "extracted_bz2"
        success = extract(str(bz2_path), str(extract_dir))
        assert success
        assert (extract_dir / "test.txt").read_bytes() == test_content
        
        echo.info("  Testing XZ...")
        xz_path = tmpdir / "test.txt.xz"
        with lzma.open(xz_path, 'wb') as f:
            f.write(test_content)
        
        fmt = detect_archive_format(str(xz_path))
        assert fmt == ArchiveFormat.XZ
        
        extract_dir = tmpdir / "extracted_xz"
        success = extract(str(xz_path), str(extract_dir))
        assert success
        assert (extract_dir / "test.txt").read_bytes() == test_content
        
        try:
            import zstandard as zstd
            
            echo.info("  Testing ZSTD...")
            zst_path = tmpdir / "test.txt.zst"
            with open(zst_path, 'wb') as f:
                cctx = zstd.ZstdCompressor()
                f.write(cctx.compress(test_content))
            
            fmt = detect_archive_format(str(zst_path))
            assert fmt == ArchiveFormat.ZSTD
            
            extract_dir = tmpdir / "extracted_zst"
            success = extract(str(zst_path), str(extract_dir))
            assert success
            assert (extract_dir / "test.txt").read_bytes() == test_content
        except ImportError:
            echo.warning("  zstandard not available, skipping ZSTD test")
    
    echo.info("Compression format extraction tests passed!")


def test_magic_bytes_with_wrong_extension():
    """Test that magic bytes detection works even with wrong file extension."""
    echo.info("\nTesting magic bytes detection with wrong extensions...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        test_dir = create_test_file_structure(tmpdir)
        
        echo.info("  Creating ZIP with .dat extension...")
        wrong_ext_path = tmpdir / "test.dat"
        create_zip(str(wrong_ext_path), [str(test_dir)], base_dir=str(tmpdir))
        
        fmt = detect_archive_format(str(wrong_ext_path))
        assert fmt == ArchiveFormat.ZIP, f"Expected ZIP by magic bytes, got {fmt}"
        
        extract_dir = tmpdir / "extracted"
        success = extract(str(wrong_ext_path), str(extract_dir))
        assert success
        verify_extracted_files(extract_dir)
    
    echo.info("Magic bytes detection test passed!")


def cleanup_test_files():
    """Clean up any leftover test files."""
    echo.info("\nCleaning up test files...")
    
    for pattern in ["test_archives", "output_*", "test_output*"]:
        for path in Path.cwd().glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                echo.info(f"  Removed {path}")
    
    echo.info("Cleanup completed!")


def test_7z_extraction():
    """Test 7z archive extraction (optional - requires py7zr)."""
    echo.info("\nTesting 7z extraction...")
    
    try:
        import py7zr
    except ImportError:
        echo.warning("  py7zr not installed, skipping 7z test")
        echo.info("  Install with: pip install py7zr")
        return
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        test_dir = create_test_file_structure(tmpdir)
        archive_path = tmpdir / "test.7z"
        
        echo.info("  Creating 7z archive...")
        with py7zr.SevenZipFile(archive_path, 'w') as archive:
            archive.writeall(test_dir, arcname='test_data')
        
        fmt = detect_archive_format(str(archive_path))
        assert fmt == ArchiveFormat.SEVEN_ZIP, f"Expected SEVEN_ZIP, got {fmt}"
        
        extract_dir = tmpdir / "extracted"
        success = extract(str(archive_path), str(extract_dir))
        assert success, "7z extraction failed"
        
        verify_extracted_files(extract_dir)
    
    echo.info("7z extraction test passed!")


if __name__ == "__main__":
    try:
        cleanup_test_files()
        print()
        
        test_format_detection()
        test_zip_extraction()
        test_tar_formats_extraction()
        test_compression_formats()
        test_magic_bytes_with_wrong_extension()
        test_7z_extraction()
        
        print()
        echo.info("=" * 60)
        echo.info("ALL TESTS PASSED SUCCESSFULLY!")
        echo.info("=" * 60)
        print()
        
        cleanup_test_files()
        
    except Exception as e:
        echo.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
