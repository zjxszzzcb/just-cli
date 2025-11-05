#!/usr/bin/env python3
"""
Test script for the linux commands functionality.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

from just.utils.shell_utils import execute_command


def setup_test_workspace():
    """Create a temporary workspace for testing."""
    test_dir = Path(tempfile.mkdtemp(prefix="test_linux_command_workspace_"))
    print(f"Created test workspace: {test_dir}")
    return test_dir


def cleanup_test_workspace(test_dir):
    """Clean up the temporary workspace."""
    if test_dir.exists():
        shutil.rmtree(test_dir)
        print(f"Cleaned up test workspace: {test_dir}")


def create_test_files(test_dir):
    """Create test files and directories for testing."""
    # Create test files
    (test_dir / "file1.txt").write_text("This is file 1.\nLine 2 of file 1.\nLine 3 of file 1.")
    (test_dir / "file2.txt").write_text("This is file 2.\nAnother line in file 2.")

    # Create a subdirectory
    subdir = test_dir / "subdir"
    subdir.mkdir()
    (subdir / "subfile.txt").write_text("This is a file in subdir.")

    # Create a hidden file
    (test_dir / ".hidden_file").write_text("This is a hidden file.")

    print("Created test files and directories.")


def test_cat_command(test_dir):
    """Test the cat command."""
    print("\n=== Testing cat command ===")

    # Test basic cat
    file_path = test_dir / "file1.txt"
    exit_code, output = execute_command(f"just cat \"{file_path}\"", capture_output=True)
    assert exit_code == 0, f"cat command failed with exit code {exit_code}"
    # Normalize line endings for comparison
    normalized_output = output.replace('\r\n', '\n')
    assert "This is file 1." in normalized_output, "cat output doesn't contain expected content"
    print("✅ Basic cat command works")

    # Test cat with line numbers
    file_path = test_dir / "file1.txt"
    exit_code, output = execute_command(f"just cat -n \"{file_path}\"", capture_output=True)
    assert exit_code == 0, f"cat -n command failed with exit code {exit_code}"
    # Normalize line endings for comparison
    normalized_output = output.replace('\r\n', '\n')
    assert "1→This is file 1." in normalized_output, "cat -n output doesn't contain numbered lines"
    print("✅ Cat command with line numbers works")

    # Test cat with non-existent file
    non_existent_file = test_dir / "nonexistent.txt"
    exit_code, output = execute_command(f"just cat \"{non_existent_file}\"", capture_output=True)
    assert exit_code != 0, "cat should fail with non-existent file"
    assert "does not exist" in output, "cat error message not found"
    print("✅ Cat command properly handles non-existent files")

    # Test cat with directory (should show error)
    subdir_path = test_dir / "subdir"
    exit_code, output = execute_command(f"just cat \"{subdir_path}\"", capture_output=True)
    assert exit_code != 0, "cat should fail when trying to read a directory"
    # Check if either error message is present (our custom message or the one from @capture_exception)
    assert "is a directory" in output or "Permission denied" in output, "cat directory error message not found"
    print("✅ Cat command properly handles directories")


def test_ls_command(test_dir):
    """Test the ls command."""
    print("\n=== Testing ls command ===")

    # Test basic ls
    exit_code, output = execute_command(f"just ls \"{test_dir}\"", capture_output=True)
    assert exit_code == 0, f"ls command failed with exit code {exit_code}"
    assert "file1.txt" in output, "ls output doesn't contain file1.txt"
    assert "file2.txt" in output, "ls output doesn't contain file2.txt"
    assert "subdir" in output, "ls output doesn't contain subdir"
    # Hidden files should not be shown by default
    assert ".hidden_file" not in output, "ls should not show hidden files by default"
    print("✅ Basic ls command works")

    # Test ls with -a flag
    exit_code, output = execute_command(f"just ls -a \"{test_dir}\"", capture_output=True)
    assert exit_code == 0, f"ls -a command failed with exit code {exit_code}"
    assert ".hidden_file" in output, "ls -a should show hidden files"
    print("✅ Ls command with -a flag works")

    # Test ls with -l flag
    exit_code, output = execute_command(f"just ls -l \"{test_dir}\"", capture_output=True)
    assert exit_code == 0, f"ls -l command failed with exit code {exit_code}"
    assert "file1.txt" in output, "ls -l output doesn't contain file1.txt"
    assert "drwxr-xr-x" in output, "ls -l should show permissions"
    print("✅ Ls command with -l flag works")

    # Test ls with non-existent directory
    non_existent_path = test_dir / "nonexistent"
    exit_code, output = execute_command(f"just ls \"{non_existent_path}\"", capture_output=True)
    assert exit_code != 0, "ls should fail with non-existent directory"
    assert "No such file or directory" in output, "ls error message not found"
    print("✅ Ls command properly handles non-existent directories")


def test_mkdir_command(test_dir):
    """Test the mkdir command."""
    print("\n=== Testing mkdir command ===")

    # Test basic mkdir
    new_dir = test_dir / "new_directory"
    exit_code, output = execute_command(f"just mkdir \"{new_dir}\"", capture_output=True)
    assert exit_code == 0, f"mkdir command failed with exit code {exit_code}"
    assert new_dir.exists(), "New directory was not created"
    print("✅ Basic mkdir command works")

    # Test mkdir with -p flag
    nested_dir = test_dir / "parent" / "child" / "grandchild"
    exit_code, output = execute_command(f"just mkdir -p \"{nested_dir}\"", capture_output=True)
    assert exit_code == 0, f"mkdir -p command failed with exit code {exit_code}"
    assert nested_dir.exists(), "Nested directory was not created with -p flag"
    print("✅ Mkdir command with -p flag works")

    # Test mkdir with existing directory (should not fail)
    exit_code, output = execute_command(f"just mkdir \"{new_dir}\"", capture_output=True)
    assert exit_code != 0, "mkdir should fail when directory already exists"
    print("✅ Mkdir command properly handles existing directories")


def test_rm_command(test_dir):
    """Test the rm command."""
    print("\n=== Testing rm command ===")

    # Create a file to remove
    file_to_remove = test_dir / "to_remove.txt"
    file_to_remove.write_text("This file will be removed.")

    # Test basic rm
    exit_code, output = execute_command(f"just rm \"{file_to_remove}\"", capture_output=True)
    assert exit_code == 0, f"rm command failed with exit code {exit_code}"
    assert not file_to_remove.exists(), "File was not removed"
    print("✅ Basic rm command works")

    # Create a directory to remove recursively
    dir_to_remove = test_dir / "dir_to_remove"
    dir_to_remove.mkdir()
    (dir_to_remove / "file_in_dir.txt").write_text("File in directory.")

    # Test rm with -r flag
    exit_code, output = execute_command(f"just rm -r \"{dir_to_remove}\"", capture_output=True)
    assert exit_code == 0, f"rm -r command failed with exit code {exit_code}"
    assert not dir_to_remove.exists(), "Directory was not removed recursively"
    print("✅ Rm command with -r flag works")

    # Test rm with non-existent file
    non_existent_file = test_dir / "nonexistent.txt"
    exit_code, output = execute_command(f"just rm \"{non_existent_file}\"", capture_output=True)
    assert exit_code != 0, "rm should fail with non-existent file"
    assert "No such file or directory" in output, "rm error message not found"
    print("✅ Rm command properly handles non-existent files")


def test_cp_command(test_dir):
    """Test the cp command."""
    print("\n=== Testing cp command ===")

    # Test basic cp (file to file)
    source_file = test_dir / "source.txt"
    source_file.write_text("This is the source file.")
    dest_file = test_dir / "dest.txt"

    exit_code, output = execute_command(f"just cp \"{source_file}\" \"{dest_file}\"", capture_output=True)
    assert exit_code == 0, f"cp command failed with exit code {exit_code}"
    assert dest_file.exists(), "Destination file was not created"
    assert dest_file.read_text() == "This is the source file.", "Copied file content doesn't match"
    print("✅ Basic cp command (file to file) works")

    # Test cp with -r flag (directory to directory)
    source_dir = test_dir / "source_dir"
    source_dir.mkdir()
    (source_dir / "file_in_source.txt").write_text("File in source directory.")

    dest_dir = test_dir / "dest_dir"

    exit_code, output = execute_command(f"just cp -r \"{source_dir}\" \"{dest_dir}\"", capture_output=True)
    assert exit_code == 0, f"cp -r command failed with exit code {exit_code}"
    assert dest_dir.exists(), "Destination directory was not created"
    assert (dest_dir / "file_in_source.txt").exists(), "File in directory was not copied"
    assert (dest_dir / "file_in_source.txt").read_text() == "File in source directory.", "Copied file content doesn't match"
    print("✅ Cp command with -r flag (directory to directory) works")

    # Test cp with non-existent source
    non_existent_file = test_dir / "nonexistent.txt"
    new_dest_file = test_dir / "new_dest.txt"
    exit_code, output = execute_command(f"just cp \"{non_existent_file}\" \"{new_dest_file}\"", capture_output=True)
    assert exit_code != 0, "cp should fail with non-existent source"
    assert "No such file or directory" in output, "cp error message not found"
    print("✅ Cp command properly handles non-existent sources")


def test_mv_command(test_dir):
    """Test the mv command."""
    print("\n=== Testing mv command ===")

    # Test basic mv (rename file)
    original_file = test_dir / "original.txt"
    original_file.write_text("This is the original file.")
    renamed_file = test_dir / "renamed.txt"

    exit_code, output = execute_command(f"just mv \"{original_file}\" \"{renamed_file}\"", capture_output=True)
    assert exit_code == 0, f"mv command failed with exit code {exit_code}"
    assert not original_file.exists(), "Original file still exists"
    assert renamed_file.exists(), "Renamed file was not created"
    assert renamed_file.read_text() == "This is the original file.", "Renamed file content doesn't match"
    print("✅ Basic mv command (rename file) works")

    # Test mv (move file to directory)
    file_to_move = test_dir / "file_to_move.txt"
    file_to_move.write_text("This file will be moved.")
    target_dir = test_dir / "target_dir"
    target_dir.mkdir()

    # Move file to target directory with a different name to avoid overwrite prompt
    target_file_path = target_dir / "moved_file.txt"
    exit_code, output = execute_command(f"just mv \"{file_to_move}\" \"{target_file_path}\"", capture_output=True)
    assert exit_code == 0, f"mv command failed with exit code {exit_code}"
    assert not file_to_move.exists(), "Original file still exists"
    assert target_file_path.exists(), "File was not moved to directory"
    assert target_file_path.read_text() == "This file will be moved.", "Moved file content doesn't match"
    print("✅ Mv command (move file to directory) works")

    # Test mv with non-existent source
    non_existent_file = test_dir / "nonexistent.txt"
    new_name_file = test_dir / "new_name.txt"
    exit_code, output = execute_command(f"just mv \"{non_existent_file}\" \"{new_name_file}\"", capture_output=True)
    assert exit_code != 0, "mv should fail with non-existent source"
    assert "No such file or directory" in output, "mv error message not found"
    print("✅ Mv command properly handles non-existent sources")


def run_all_tests():
    """Run all linux command tests."""
    print("Running linux commands tests...")

    # Setup
    test_dir = setup_test_workspace()
    try:
        create_test_files(test_dir)

        # Change to test directory for relative path tests
        original_cwd = os.getcwd()
        os.chdir(test_dir)

        try:
            # Run tests
            test_cat_command(test_dir)
            test_ls_command(test_dir)
            test_mkdir_command(test_dir)
            test_rm_command(test_dir)
            test_cp_command(test_dir)
            test_mv_command(test_dir)

            print("\n🎉 All tests passed!")
            return True

        finally:
            # Restore original working directory
            os.chdir(original_cwd)

    except Exception as e:
        print(f"❌ Tests failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Cleanup
        cleanup_test_workspace(test_dir)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)