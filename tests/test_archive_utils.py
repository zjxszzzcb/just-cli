import tempfile
import shutil
from pathlib import Path

from just.utils.zip_utils import extract_zip, create_zip
from just.utils.tar_utils import extract_tar, create_tar
import just.utils.echo_utils as echo


def test_zip():
    echo.info("Testing zip utilities...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        test_dir = tmpdir / "test_data"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("Hello from file1")
        (test_dir / "file2.txt").write_text("Hello from file2")
        
        subdir = test_dir / "subdir"
        subdir.mkdir()
        (subdir / "file3.txt").write_text("Hello from subdir")
        
        archive_path = tmpdir / "test.zip"
        echo.info(f"Creating zip archive: {archive_path}")
        success = create_zip(str(archive_path), [str(test_dir)], base_dir=str(tmpdir))
        assert success, "Failed to create zip archive"
        assert archive_path.exists(), "Archive file was not created"
        
        extract_dir = tmpdir / "extracted"
        echo.info(f"Extracting zip archive to: {extract_dir}")
        success = extract_zip(str(archive_path), str(extract_dir))
        assert success, "Failed to extract zip archive"
        
        assert (extract_dir / "test_data" / "file1.txt").exists()
        assert (extract_dir / "test_data" / "file2.txt").exists()
        assert (extract_dir / "test_data" / "subdir" / "file3.txt").exists()
        
        content = (extract_dir / "test_data" / "file1.txt").read_text()
        assert content == "Hello from file1"
        
        echo.info("Zip utilities test passed!")


def test_tar_formats():
    echo.info("Testing tar utilities with various formats...")
    
    formats = [
        ('test.tar', None),
        ('test.tar.gz', 'gz'),
        ('test.tgz', 'gz'),
        ('test.tar.xz', 'xz'),
        ('test.tar.bz2', 'bz2'),
    ]
    
    try:
        import zstandard
        formats.append(('test.tar.zst', 'zst'))
        echo.info("zstandard available, will test .tar.zst format")
    except ImportError:
        echo.warning("zstandard not available, skipping .tar.zst test")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        test_dir = tmpdir / "test_data"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("Hello from file1")
        (test_dir / "file2.txt").write_text("Hello from file2")
        
        subdir = test_dir / "subdir"
        subdir.mkdir()
        (subdir / "file3.txt").write_text("Hello from subdir")
        
        for archive_name, compression in formats:
            echo.info(f"\nTesting format: {archive_name}")
            
            archive_path = tmpdir / archive_name
            echo.info(f"  Creating tar archive: {archive_path}")
            success = create_tar(str(archive_path), [str(test_dir)], compression=compression, base_dir=str(tmpdir))
            assert success, f"Failed to create {archive_name}"
            assert archive_path.exists(), f"Archive file {archive_name} was not created"
            
            extract_dir = tmpdir / f"extracted_{archive_name}"
            echo.info(f"  Extracting tar archive to: {extract_dir}")
            success = extract_tar(str(archive_path), str(extract_dir))
            assert success, f"Failed to extract {archive_name}"
            
            assert (extract_dir / "test_data" / "file1.txt").exists()
            assert (extract_dir / "test_data" / "file2.txt").exists()
            assert (extract_dir / "test_data" / "subdir" / "file3.txt").exists()
            
            content = (extract_dir / "test_data" / "file1.txt").read_text()
            assert content == "Hello from file1"
            
            echo.info(f"  Format {archive_name} test passed!")
    
    echo.info("All tar format tests passed!")


def cleanup_test_files():
    """
    Clean up test archives and output directories.
    """
    echo.info("Cleaning up test files...")
    
    test_archives_dir = Path("test_archives")
    if test_archives_dir.exists():
        shutil.rmtree(test_archives_dir)
        echo.info(f"  Removed {test_archives_dir}")
    
    for pattern in ["output_*", "test_output*"]:
        for path in Path.cwd().glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                echo.info(f"  Removed {path}")
    
    echo.info("Cleanup completed!")


def create_test_archives():
    """
    Create test archives in various formats.
    """
    echo.info("Creating test archives...")
    
    test_dir = Path("test_archives")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()
    
    data_dir = test_dir / "test_data"
    data_dir.mkdir()
    (data_dir / "file1.txt").write_text("Hello from file1")
    (data_dir / "file2.txt").write_text("Hello from file2")
    
    subdir = data_dir / "subdir"
    subdir.mkdir()
    (subdir / "file3.txt").write_text("Hello from subdir")
    
    archives = []
    
    echo.info("  Creating test.zip...")
    create_zip(str(test_dir / "test.zip"), [str(data_dir)], base_dir=str(test_dir))
    archives.append("test.zip")
    
    echo.info("  Creating test.tar...")
    create_tar(str(test_dir / "test.tar"), [str(data_dir)], compression=None, base_dir=str(test_dir))
    archives.append("test.tar")
    
    echo.info("  Creating test.tar.gz...")
    create_tar(str(test_dir / "test.tar.gz"), [str(data_dir)], compression='gz', base_dir=str(test_dir))
    archives.append("test.tar.gz")
    
    echo.info("  Creating test.tgz...")
    create_tar(str(test_dir / "test.tgz"), [str(data_dir)], compression='gz', base_dir=str(test_dir))
    archives.append("test.tgz")
    
    echo.info("  Creating test.tar.xz...")
    create_tar(str(test_dir / "test.tar.xz"), [str(data_dir)], compression='xz', base_dir=str(test_dir))
    archives.append("test.tar.xz")
    
    try:
        import zstandard
        echo.info("  Creating test.tar.zst...")
        create_tar(str(test_dir / "test.tar.zst"), [str(data_dir)], compression='zst', base_dir=str(test_dir))
        archives.append("test.tar.zst")
    except ImportError:
        echo.warning("  zstandard not available, skipping test.tar.zst")
    
    shutil.rmtree(data_dir)
    
    echo.info(f"Created {len(archives)} test archives in {test_dir}/")
    return archives


if __name__ == "__main__":
    try:
        cleanup_test_files()
        print()
        
        create_test_archives()
        print()
        
        test_zip()
        print()
        
        test_tar_formats()
        print()
        
        echo.info("All tests passed successfully!")
        print()
        
        cleanup_test_files()
        
    except Exception as e:
        echo.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
