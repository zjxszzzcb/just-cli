#!/usr/bin/env python3
"""
Test script for the download functionality.
"""

import os
import sys
import tempfile
import shutil
import time
from pathlib import Path

# Add the src directory to the path so we can import the download module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from just.utils.download_utils import download_with_resume
from just.utils.shell_utils import execute_command


def setup_test_workspace():
    """Create a temporary workspace for testing."""
    # Create test workspace in tests/ directory instead of system temp directory
    tests_dir = Path(__file__).parent
    test_dir = Path(tempfile.mkdtemp(prefix="test_download_workspace_", dir=tests_dir))
    print(f"Created test workspace: {test_dir}")
    return test_dir


def cleanup_test_workspace(test_dir):
    """Clean up the temporary workspace."""
    if test_dir.exists():
        shutil.rmtree(test_dir)
        print(f"Cleaned up test workspace: {test_dir}")


def cleanup_downloaded_files():
    """Clean up downloaded files in current directory."""
    files_to_clean = [
        "tokenizer.json",
        "tokenizer_direct.json",
        "tokenizer_partial_direct.json",
        "tokenizer_partial_command.json",
        "tokenizer_headers.json",
        "nonexistent.json"
    ]

    for file in files_to_clean:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"Cleaned up file: {file}")
            except Exception as e:
                print(f"Failed to clean up {file}: {e}")


def test_direct_download_complete(test_dir):
    """Test complete download using direct function call."""
    print("\n=== Testing direct download complete ===")

    # Test file URL
    url = "https://www.modelscope.cn/models/Qwen/Qwen3-0.6B/resolve/master/tokenizer.json"
    output_file = str(test_dir / "tokenizer_direct.json")

    # Perform download
    success = download_with_resume(url, {}, output_file, verbose=True)

    # Verify download
    assert success, "Direct download failed"
    assert os.path.exists(output_file), "Output file was not created"
    assert os.path.getsize(output_file) > 0, "Output file is empty"

    print("✅ Direct download complete test passed")
    return output_file


def test_command_download_complete(test_dir):
    """Test complete download using just command."""
    print("\n=== Testing command download complete ===")

    # Clean up any existing file first
    output_file = "tokenizer.json"  # Download to current directory
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"Removed existing file: {output_file}")

    # Test file URL
    url = "https://www.modelscope.cn/models/Qwen/Qwen3-0.6B/resolve/master/tokenizer.json"

    # Perform download using just command
    exit_code, output = execute_command(
        f"just download \"{url}\" -o \"{output_file}\" --verbose",
        capture_output=True
    )

    # Verify download
    assert exit_code == 0, f"Just command download failed with exit code {exit_code}: {output}"
    assert os.path.exists(output_file), "Output file was not created"
    assert os.path.getsize(output_file) > 0, "Output file is empty"

    print("✅ Command download complete test passed")
    return output_file


def test_direct_download_resume(test_dir, reference_file):
    """Test resume download using direct function call."""
    print("\n=== Testing direct download resume ===")

    # Create a partial file by copying first 1000 bytes of reference file
    partial_file = str(test_dir / "tokenizer_partial_direct.json")
    with open(reference_file, 'rb') as src, open(partial_file, 'wb') as dst:
        dst.write(src.read(1000))  # Copy first 1000 bytes

    # Verify partial file creation
    assert os.path.exists(partial_file), "Partial file was not created"
    partial_size = os.path.getsize(partial_file)
    assert partial_size == 1000, f"Partial file size is {partial_size}, expected 1000"

    # Test file URL
    url = "https://www.modelscope.cn/models/Qwen/Qwen3-0.6B/resolve/master/tokenizer.json"

    # Perform download (should resume)
    success = download_with_resume(url, {}, partial_file, verbose=True)

    # Verify download
    assert success, "Resume download failed"
    assert os.path.exists(partial_file), "Output file was not created after resume"
    final_size = os.path.getsize(partial_file)
    assert final_size > partial_size, f"File size didn't increase after resume: {final_size} <= {partial_size}"
    assert final_size == os.path.getsize(reference_file), f"Final file size {final_size} doesn't match reference {os.path.getsize(reference_file)}"

    print("✅ Direct download resume test passed")


def test_command_download_resume(test_dir, reference_file):
    """Test resume download using just command."""
    print("\n=== Testing command download resume ===")

    # Clean up any existing file first
    partial_file = "tokenizer_partial_command.json"  # Download to current directory
    if os.path.exists(partial_file):
        os.remove(partial_file)
        print(f"Removed existing file: {partial_file}")

    # Create a partial file by copying first 1000 bytes of reference file
    with open(reference_file, 'rb') as src, open(partial_file, 'wb') as dst:
        dst.write(src.read(1000))  # Copy first 1000 bytes

    # Verify partial file creation
    assert os.path.exists(partial_file), "Partial file was not created"
    partial_size = os.path.getsize(partial_file)
    assert partial_size == 1000, f"Partial file size is {partial_size}, expected 1000"

    # Test file URL
    url = "https://www.modelscope.cn/models/Qwen/Qwen3-0.6B/resolve/master/tokenizer.json"

    # Perform download using just command (should resume)
    exit_code, output = execute_command(
        f"just download \"{url}\" -o \"{partial_file}\" --verbose",
        capture_output=True
    )

    # Verify download
    assert exit_code == 0, f"Just command resume download failed with exit code {exit_code}: {output}"
    assert os.path.exists(partial_file), "Output file was not created after resume"
    final_size = os.path.getsize(partial_file)
    assert final_size > partial_size, f"File size didn't increase after resume: {final_size} <= {partial_size}"
    assert final_size == os.path.getsize(reference_file), f"Final file size {final_size} doesn't match reference {os.path.getsize(reference_file)}"

    print("✅ Command download resume test passed")


def test_download_with_custom_headers(test_dir):
    """Test download with custom headers."""
    print("\n=== Testing download with custom headers ===")

    # Test file URL
    url = "https://www.modelscope.cn/models/Qwen/Qwen3-0.6B/resolve/master/tokenizer.json"
    output_file = str(test_dir / "tokenizer_headers.json")

    # Custom headers
    headers = {
        "User-Agent": "JUST-CLI-Test/1.0",
        "Accept": "application/json"
    }

    # Perform download
    success = download_with_resume(url, headers, output_file, verbose=True)

    # Verify download
    assert success, "Download with custom headers failed"
    assert os.path.exists(output_file), "Output file was not created"
    assert os.path.getsize(output_file) > 0, "Output file is empty"

    print("✅ Download with custom headers test passed")


def test_download_nonexistent_url(test_dir):
    """Test download with nonexistent URL."""
    print("\n=== Testing download nonexistent URL ===")

    # Nonexistent URL
    url = "https://www.modelscope.cn/models/Qwen/Qwen3-0.6B/resolve/master/nonexistent.json"
    output_file = str(test_dir / "nonexistent.json")

    # Perform download
    success = download_with_resume(url, {}, output_file, verbose=True)

    # Verify download failed
    assert not success, "Download should have failed for nonexistent URL"
    # File may or may not exist depending on when the error occurred

    print("✅ Download nonexistent URL test passed")


def run_all_tests():
    """Run all download tests."""
    print("Running download tests...")

    # Setup
    test_dir = setup_test_workspace()
    reference_file = None

    try:
        # Run tests
        reference_file = test_direct_download_complete(test_dir)
        test_command_download_complete(test_dir)
        test_direct_download_resume(test_dir, reference_file)
        test_command_download_resume(test_dir, reference_file)
        test_download_with_custom_headers(test_dir)
        test_download_nonexistent_url(test_dir)

        print("\n🎉 All download tests passed!")
        return True

    except Exception as e:
        print(f"❌ Tests failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Cleanup
        cleanup_test_workspace(test_dir)
        cleanup_downloaded_files()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)