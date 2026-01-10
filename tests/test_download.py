#!/usr/bin/env python3
"""
Download Utilities Test Suite
=============================

Tests core download functionality: complete download and resume support.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

from just.utils.download_utils import download_with_resume


# ModelScope tokenizer.json as test file
TEST_URL = "https://www.modelscope.cn/models/Qwen/Qwen3-0.6B/resolve/master/tokenizer.json"


def setup_test_workspace():
    """Create a temporary workspace for testing."""
    tests_dir = Path(__file__).parent
    test_dir = Path(tempfile.mkdtemp(prefix="test_download_", dir=tests_dir))
    print(f"Created test workspace: {test_dir}")
    return test_dir


def cleanup_test_workspace(test_dir):
    """Clean up the temporary workspace."""
    if test_dir.exists():
        shutil.rmtree(test_dir)
        print(f"Cleaned up test workspace: {test_dir}")


def test_download_complete(test_dir):
    """
    Test: Complete Download
    =======================
    
    Verifies that download_with_resume can download a file completely.
    """
    print("\n=== Testing complete download ===")

    output_file = str(test_dir / "tokenizer.json")

    success = download_with_resume(
        TEST_URL, 
        {"Accept-Encoding": "identity"}, 
        output_file, 
        verbose=True
    )

    assert success, "Download failed"
    assert os.path.exists(output_file), "Output file was not created"
    
    file_size = os.path.getsize(output_file)
    assert file_size > 0, "Output file is empty"

    print(f"✅ Complete download test passed (size: {file_size} bytes)")
    return output_file, file_size


def test_download_resume(test_dir, reference_file, expected_size):
    """
    Test: Resume Download
    =====================
    
    Verifies that download can resume from a partial file.
    """
    print("\n=== Testing resume download ===")

    partial_file = str(test_dir / "tokenizer_partial.json")
    temp_file = partial_file + ".tmp"
    
    # Create a partial TEMP file (first 1000 bytes)
    with open(reference_file, 'rb') as src, open(temp_file, 'wb') as dst:
        dst.write(src.read(1000))

    partial_size = os.path.getsize(temp_file)
    assert partial_size == 1000, f"Partial file size is {partial_size}, expected 1000"
    print(f"Created partial file: {partial_size} bytes")

    # Resume download
    success = download_with_resume(
        TEST_URL, 
        {"Accept-Encoding": "identity"}, 
        partial_file, 
        verbose=True
    )

    assert success, "Resume download failed"
    assert os.path.exists(partial_file), "Output file was not created"
    assert not os.path.exists(temp_file), "Temp file should be removed"
    
    final_size = os.path.getsize(partial_file)
    assert final_size == expected_size, f"Size mismatch: {final_size} vs {expected_size}"

    print(f"✅ Resume download test passed (final size: {final_size} bytes)")


def run_all_tests():
    """Run all download tests."""
    print("Running download tests...\n")

    test_dir = setup_test_workspace()

    try:
        # Test 1: Complete download
        reference_file, expected_size = test_download_complete(test_dir)
        
        # Test 2: Resume download
        test_download_resume(test_dir, reference_file, expected_size)

        print("\n🎉 All download tests passed!")
        return True

    except Exception as e:
        print(f"❌ Tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        cleanup_test_workspace(test_dir)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)