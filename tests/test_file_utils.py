#!/usr/bin/env python3
"""
Test script for file_utils module functionality.
"""

import sys
import tempfile
import os
from pathlib import Path

# Add the src directory to the path so we can import just modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from just.utils.file_utils import mkdir, mv, rm, write_file, symlink


def can_create_symlinks():
    """Check if the current user can create symbolic links."""
    with tempfile.TemporaryDirectory() as temp_dir:
        src = Path(temp_dir) / "test_src"
        src.touch()
        link = Path(temp_dir) / "test_link"
        try:
            os.symlink(src, link)
            return True
        except OSError:
            return False


def test_mkdir_single():
    """Test creating a single directory."""
    print("Testing mkdir with single directory...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir) / "test_dir" / "nested" / "deep"
        
        # Create nested directory
        mkdir(str(test_dir))
        
        # Verify it exists
        assert test_dir.exists()
        assert test_dir.is_dir()
    
    print("✅ mkdir single directory test passed")


def test_mkdir_multiple():
    """Test creating multiple directories."""
    print("Testing mkdir with multiple directories...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dirs = [
            Path(temp_dir) / "dir1" / "nested1",
            Path(temp_dir) / "dir2" / "nested2",
            Path(temp_dir) / "dir3"
        ]
        
        # Create multiple directories
        mkdir(*[str(d) for d in test_dirs])
        
        # Verify all exist
        for test_dir in test_dirs:
            assert test_dir.exists()
            assert test_dir.is_dir()
    
    print("✅ mkdir multiple directories test passed")


def test_mkdir_existing():
    """Test mkdir with existing directory (should not fail)."""
    print("Testing mkdir with existing directory...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir) / "existing"
        test_dir.mkdir()
        
        # Try to create the same directory again (should not raise error)
        mkdir(str(test_dir))
        
        assert test_dir.exists()
    
    print("✅ mkdir existing directory test passed")


def test_mv_file():
    """Test moving/renaming a file."""
    print("Testing mv with file...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        src_file = Path(temp_dir) / "source.txt"
        dst_file = Path(temp_dir) / "destination.txt"
        
        # Create source file
        write_file(str(src_file), "test content")
        
        # Move file
        mv(str(src_file), str(dst_file))
        
        # Verify source no longer exists and destination exists
        assert not src_file.exists()
        assert dst_file.exists()
        assert dst_file.read_text() == "test content"
    
    print("✅ mv file test passed")


def test_mv_directory():
    """Test moving/renaming a directory."""
    print("Testing mv with directory...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        src_dir = Path(temp_dir) / "source_dir"
        dst_dir = Path(temp_dir) / "destination_dir"
        
        # Create source directory with a file
        src_dir.mkdir()
        test_file = src_dir / "test.txt"
        write_file(str(test_file), "test content")
        
        # Move directory
        mv(str(src_dir), str(dst_dir))
        
        # Verify source no longer exists and destination exists with content
        assert not src_dir.exists()
        assert dst_dir.exists()
        assert (dst_dir / "test.txt").exists()
        assert (dst_dir / "test.txt").read_text() == "test content"
    
    print("✅ mv directory test passed")


def test_mv_to_directory():
    """Test moving a file into a directory."""
    print("Testing mv file into directory...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        src_file = Path(temp_dir) / "file.txt"
        dst_dir = Path(temp_dir) / "target_dir"
        dst_dir.mkdir()
        
        # Create source file
        write_file(str(src_file), "test content")
        
        # Move file into directory
        mv(str(src_file), str(dst_dir))
        
        # Verify file is now in destination directory
        assert not src_file.exists()
        assert (dst_dir / "file.txt").exists()
        assert (dst_dir / "file.txt").read_text() == "test content"
    
    print("✅ mv file into directory test passed")


def test_rm_single_file():
    """Test removing a single file."""
    print("Testing rm with single file...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "test.txt"
        write_file(str(test_file), "test content")
        
        # Remove file
        rm(str(test_file))
        
        # Verify it no longer exists
        assert not test_file.exists()
    
    print("✅ rm single file test passed")


def test_rm_single_directory():
    """Test removing a single directory."""
    print("Testing rm with single directory...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir) / "test_dir"
        test_dir.mkdir()
        
        # Create files inside
        (test_dir / "file1.txt").write_text("content1")
        (test_dir / "file2.txt").write_text("content2")
        
        # Remove directory
        rm(str(test_dir))
        
        # Verify it no longer exists
        assert not test_dir.exists()
    
    print("✅ rm single directory test passed")


def test_rm_multiple_targets():
    """Test removing multiple files and directories."""
    print("Testing rm with multiple targets...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        file1 = Path(temp_dir) / "file1.txt"
        file2 = Path(temp_dir) / "file2.txt"
        dir1 = Path(temp_dir) / "dir1"
        dir2 = Path(temp_dir) / "dir2"
        
        # Create test files and directories
        write_file(str(file1), "content1")
        write_file(str(file2), "content2")
        dir1.mkdir()
        dir2.mkdir()
        (dir2 / "nested.txt").write_text("nested content")
        
        # Remove all targets
        rm(str(file1), str(file2), str(dir1), str(dir2))
        
        # Verify all are removed
        assert not file1.exists()
        assert not file2.exists()
        assert not dir1.exists()
        assert not dir2.exists()
    
    print("✅ rm multiple targets test passed")


def test_rm_nested_directory():
    """Test removing a nested directory structure."""
    print("Testing rm with nested directory...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir) / "parent" / "child" / "grandchild"
        test_dir.mkdir(parents=True)
        
        # Create files at different levels
        (Path(temp_dir) / "parent" / "file1.txt").write_text("content1")
        (Path(temp_dir) / "parent" / "child" / "file2.txt").write_text("content2")
        (test_dir / "file3.txt").write_text("content3")
        
        # Remove parent directory
        rm(str(Path(temp_dir) / "parent"))
        
        # Verify entire tree is removed
        assert not (Path(temp_dir) / "parent").exists()
    
    print("✅ rm nested directory test passed")


def test_symlink_file():
    """Test creating a symlink to a file."""
    print("Testing symlink with file...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        src_file = Path(temp_dir) / "source.txt"
        link_file = Path(temp_dir) / "link.txt"
        
        # Create source file
        write_file(str(src_file), "test content")
        
        # Create symlink
        symlink(str(src_file), str(link_file))
        
        # Verify symlink exists and points to correct file
        assert link_file.exists()
        assert link_file.is_symlink()
        assert link_file.read_text() == "test content"
        assert link_file.resolve() == src_file.resolve()
    
    print("✅ symlink file test passed")


def test_symlink_directory():
    """Test creating a symlink to a directory."""
    print("Testing symlink with directory...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        src_dir = Path(temp_dir) / "source_dir"
        link_dir = Path(temp_dir) / "link_dir"
        
        # Create source directory with a file
        src_dir.mkdir()
        test_file = src_dir / "test.txt"
        write_file(str(test_file), "test content")
        
        # Create symlink
        symlink(str(src_dir), str(link_dir))
        
        # Verify symlink exists and points to correct directory
        assert link_dir.exists()
        assert link_dir.is_symlink()
        assert (link_dir / "test.txt").exists()
        assert (link_dir / "test.txt").read_text() == "test content"
        assert link_dir.resolve() == src_dir.resolve()
    
    print("✅ symlink directory test passed")


def test_symlink_relative_path():
    """Test creating a symlink with relative paths."""
    print("Testing symlink with relative paths...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        src_file = Path(temp_dir) / "source.txt"
        link_file = Path(temp_dir) / "subdir" / "link.txt"
        link_file.parent.mkdir()
        
        # Create source file
        write_file(str(src_file), "test content")
        
        # Create symlink with absolute paths
        symlink(str(src_file), str(link_file))
        
        # Verify symlink works
        assert link_file.exists()
        assert link_file.is_symlink()
        assert link_file.read_text() == "test content"
    
    print("✅ symlink relative path test passed")


def run_all_tests():
    """Run all tests."""
    print("Running file_utils tests...\n")
    
    # Check if symlinks can be created
    symlink_support = can_create_symlinks()
    if not symlink_support:
        print("⚠️  Warning: Symlink creation not supported (requires admin privileges on Windows)")
    
    tests = [
        test_mkdir_single,
        test_mkdir_multiple,
        test_mkdir_existing,
        test_mv_file,
        test_mv_directory,
        test_mv_to_directory,
        test_rm_single_file,
        test_rm_single_directory,
        test_rm_multiple_targets,
        test_rm_nested_directory,
    ]
    
    # Only add symlink tests if supported
    if symlink_support:
        tests.extend([
            test_symlink_file,
            test_symlink_directory,
            test_symlink_relative_path
        ])
    
    passed = 0
    failed = 0
    skipped = 0 if symlink_support else 3
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    if skipped > 0:
        print(f"\nResults: {passed} passed, {failed} failed, {skipped} skipped")
    else:
        print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
