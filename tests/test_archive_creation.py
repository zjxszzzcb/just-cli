"""Tests for archive creation (just archive)."""
import tempfile
from pathlib import Path

from just.utils.archive import (
    archive,
    extract,
    detect_format_by_extension,
    ArchiveFormat,
)
import just.utils.echo_utils as echo


def create_test_file_structure(base_dir: Path) -> Path:
    """Create test file structure for archiving."""
    test_dir = base_dir / "test_data"
    test_dir.mkdir()
    (test_dir / "file1.txt").write_text("Hello from file1")
    (test_dir / "file2.txt").write_text("Hello from file2")

    subdir = test_dir / "subdir"
    subdir.mkdir()
    (subdir / "file3.txt").write_text("Hello from subdir")

    return test_dir


def verify_roundtrip(archive_path: str, expected_files: dict[str, str]):
    """
    Extract archive and verify file contents match expected.
    expected_files: {relative_path: expected_content}
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        success = extract(archive_path, tmpdir)
        assert success, f"Failed to extract {archive_path}"

        extract_dir = Path(tmpdir)
        for rel_path, expected_content in expected_files.items():
            file_path = extract_dir / rel_path
            assert file_path.exists(), f"Missing file: {rel_path}"
            assert file_path.read_text() == expected_content, f"Content mismatch: {rel_path}"


def test_format_detection_by_output():
    """Test that output extension maps to correct format."""
    assert detect_format_by_extension("out.zip") == ArchiveFormat.ZIP
    assert detect_format_by_extension("out.tar") == ArchiveFormat.TAR
    assert detect_format_by_extension("out.tar.gz") == ArchiveFormat.TAR_GZ
    assert detect_format_by_extension("out.tgz") == ArchiveFormat.TAR_GZ
    assert detect_format_by_extension("out.tar.bz2") == ArchiveFormat.TAR_BZ2
    assert detect_format_by_extension("out.tar.xz") == ArchiveFormat.TAR_XZ
    assert detect_format_by_extension("out.gz") == ArchiveFormat.GZIP
    assert detect_format_by_extension("out.bz2") == ArchiveFormat.BZIP2
    assert detect_format_by_extension("out.xz") == ArchiveFormat.XZ
    assert detect_format_by_extension("out.7z") == ArchiveFormat.SEVEN_ZIP
    assert detect_format_by_extension("out.unknown") is None


def test_zip_archive_roundtrip():
    """Test ZIP archive creation and extraction."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        test_dir = create_test_file_structure(tmpdir)
        output = tmpdir / "test.zip"

        success = archive([str(test_dir)], str(output), base_dir=str(tmpdir))
        assert success, "ZIP creation failed"
        assert output.exists(), "Output file not created"

        verify_roundtrip(str(output), {
            "test_data/file1.txt": "Hello from file1",
            "test_data/file2.txt": "Hello from file2",
            "test_data/subdir/file3.txt": "Hello from subdir",
        })


def test_tar_archive_roundtrip():
    """Test TAR archive creation and extraction (uncompressed)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        test_dir = create_test_file_structure(tmpdir)
        output = tmpdir / "test.tar"

        success = archive([str(test_dir)], str(output), base_dir=str(tmpdir))
        assert success, "TAR creation failed"

        verify_roundtrip(str(output), {
            "test_data/file1.txt": "Hello from file1",
            "test_data/file2.txt": "Hello from file2",
            "test_data/subdir/file3.txt": "Hello from subdir",
        })


def test_tar_gz_archive_roundtrip():
    """Test tar.gz archive creation and extraction."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        test_dir = create_test_file_structure(tmpdir)
        output = tmpdir / "test.tar.gz"

        success = archive([str(test_dir)], str(output), base_dir=str(tmpdir))
        assert success, "tar.gz creation failed"

        verify_roundtrip(str(output), {
            "test_data/file1.txt": "Hello from file1",
            "test_data/file2.txt": "Hello from file2",
            "test_data/subdir/file3.txt": "Hello from subdir",
        })


def test_tar_bz2_archive_roundtrip():
    """Test tar.bz2 archive creation and extraction."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        test_dir = create_test_file_structure(tmpdir)
        output = tmpdir / "test.tar.bz2"

        success = archive([str(test_dir)], str(output), base_dir=str(tmpdir))
        assert success, "tar.bz2 creation failed"

        verify_roundtrip(str(output), {
            "test_data/file1.txt": "Hello from file1",
            "test_data/file2.txt": "Hello from file2",
            "test_data/subdir/file3.txt": "Hello from subdir",
        })


def test_tar_xz_archive_roundtrip():
    """Test tar.xz archive creation and extraction."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        test_dir = create_test_file_structure(tmpdir)
        output = tmpdir / "test.tar.xz"

        success = archive([str(test_dir)], str(output), base_dir=str(tmpdir))
        assert success, "tar.xz creation failed"

        verify_roundtrip(str(output), {
            "test_data/file1.txt": "Hello from file1",
            "test_data/file2.txt": "Hello from file2",
            "test_data/subdir/file3.txt": "Hello from subdir",
        })


def test_tar_zst_archive_roundtrip():
    """Test tar.zst archive creation and extraction."""
    try:
        import zstandard
    except ImportError:
        echo.warning("zstandard not available, skipping tar.zst test")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        test_dir = create_test_file_structure(tmpdir)
        output = tmpdir / "test.tar.zst"

        success = archive([str(test_dir)], str(output), base_dir=str(tmpdir))
        assert success, "tar.zst creation failed"

        verify_roundtrip(str(output), {
            "test_data/file1.txt": "Hello from file1",
            "test_data/file2.txt": "Hello from file2",
            "test_data/subdir/file3.txt": "Hello from subdir",
        })


def test_gzip_single_file_roundtrip():
    """Test gzip single file compression and extraction."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        source = tmpdir / "test.txt"
        source.write_text("Hello gzip")
        output = tmpdir / "test.txt.gz"

        success = archive([str(source)], str(output))
        assert success, "gzip creation failed"
        assert output.exists()

        extract_dir = tmpdir / "extracted"
        success = extract(str(output), str(extract_dir))
        assert success
        assert (extract_dir / "test.txt").read_text() == "Hello gzip"


def test_bzip2_single_file_roundtrip():
    """Test bzip2 single file compression and extraction."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        source = tmpdir / "test.txt"
        source.write_text("Hello bzip2")
        output = tmpdir / "test.txt.bz2"

        success = archive([str(source)], str(output))
        assert success, "bzip2 creation failed"

        extract_dir = tmpdir / "extracted"
        success = extract(str(output), str(extract_dir))
        assert success
        assert (extract_dir / "test.txt").read_text() == "Hello bzip2"


def test_xz_single_file_roundtrip():
    """Test xz single file compression and extraction."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        source = tmpdir / "test.txt"
        source.write_text("Hello xz")
        output = tmpdir / "test.txt.xz"

        success = archive([str(source)], str(output))
        assert success, "xz creation failed"

        extract_dir = tmpdir / "extracted"
        success = extract(str(output), str(extract_dir))
        assert success
        assert (extract_dir / "test.txt").read_text() == "Hello xz"


def test_zstd_single_file_roundtrip():
    """Test zstd single file compression and extraction."""
    try:
        import zstandard
    except ImportError:
        echo.warning("zstandard not available, skipping zstd test")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        source = tmpdir / "test.txt"
        source.write_text("Hello zstd")
        output = tmpdir / "test.txt.zst"

        success = archive([str(source)], str(output))
        assert success, "zstd creation failed"

        extract_dir = tmpdir / "extracted"
        success = extract(str(output), str(extract_dir))
        assert success
        assert (extract_dir / "test.txt").read_text() == "Hello zstd"


def test_7z_archive_roundtrip():
    """Test 7z archive creation and extraction."""
    try:
        import py7zr
    except ImportError:
        echo.warning("py7zr not available, skipping 7z test")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        test_dir = create_test_file_structure(tmpdir)
        output = tmpdir / "test.7z"

        success = archive([str(test_dir)], str(output), base_dir=str(tmpdir))
        assert success, "7z creation failed"

        verify_roundtrip(str(output), {
            "test_data/file1.txt": "Hello from file1",
            "test_data/file2.txt": "Hello from file2",
            "test_data/subdir/file3.txt": "Hello from subdir",
        })


def test_single_file_format_rejects_directory():
    """Test that single-file formats reject directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        test_dir = create_test_file_structure(tmpdir)
        output = tmpdir / "test.gz"

        success = archive([str(test_dir)], str(output))
        assert not success, "Should reject directory for gzip format"


def test_single_file_format_rejects_multiple_sources():
    """Test that single-file formats reject multiple source files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        f1 = tmpdir / "a.txt"
        f2 = tmpdir / "b.txt"
        f1.write_text("a")
        f2.write_text("b")
        output = tmpdir / "test.gz"

        success = archive([str(f1), str(f2)], str(output))
        assert not success, "Should reject multiple sources for gzip format"


def test_unknown_format_rejected():
    """Test that unknown output format is rejected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        source = tmpdir / "test.txt"
        source.write_text("test")
        output = tmpdir / "test.xyz"

        success = archive([str(source)], str(output))
        assert not success, "Should reject unknown format"


def test_source_not_found():
    """Test that missing source file is rejected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output = Path(tmpdir) / "test.gz"
        success = archive(["/nonexistent/file.txt"], str(output))
        assert not success, "Should reject missing source"


if __name__ == "__main__":
    try:
        print()
        test_format_detection_by_output()
        echo.info("Format detection test passed!")

        test_zip_archive_roundtrip()
        echo.info("ZIP roundtrip test passed!")

        test_tar_archive_roundtrip()
        echo.info("TAR roundtrip test passed!")

        test_tar_gz_archive_roundtrip()
        echo.info("TAR.GZ roundtrip test passed!")

        test_tar_bz2_archive_roundtrip()
        echo.info("TAR.BZ2 roundtrip test passed!")

        test_tar_xz_archive_roundtrip()
        echo.info("TAR.XZ roundtrip test passed!")

        test_tar_zst_archive_roundtrip()
        echo.info("TAR.ZST roundtrip test passed!")

        test_gzip_single_file_roundtrip()
        echo.info("GZIP roundtrip test passed!")

        test_bzip2_single_file_roundtrip()
        echo.info("BZIP2 roundtrip test passed!")

        test_xz_single_file_roundtrip()
        echo.info("XZ roundtrip test passed!")

        test_zstd_single_file_roundtrip()
        echo.info("ZSTD roundtrip test passed!")

        test_7z_archive_roundtrip()
        echo.info("7Z roundtrip test passed!")

        test_single_file_format_rejects_directory()
        echo.info("Directory rejection test passed!")

        test_single_file_format_rejects_multiple_sources()
        echo.info("Multiple sources rejection test passed!")

        test_unknown_format_rejected()
        echo.info("Unknown format rejection test passed!")

        test_source_not_found()
        echo.info("Source not found test passed!")

        print()
        echo.info("=" * 60)
        echo.info("ALL ARCHIVE CREATION TESTS PASSED!")
        echo.info("=" * 60)
        print()

    except Exception as e:
        echo.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
