#!/usr/bin/env python3
"""
Test Runner for JUST CLI
========================

This script acts as both an orchestrator and a test runner.
- Default mode: Orchestrates tests (Docker + Local if Windows).
- Worker mode (--worker): Runs the actual unit tests.
"""

import sys
import os
import time
import subprocess
import platform
import argparse
from pathlib import Path

# Ensure stdout is unbuffered
sys.stdout.reconfigure(line_buffering=True)

def run_actual_tests():
    """Discover and run tests (Worker Mode)."""
    start_time = time.time()
    # If running from project root, tests are in tests/
    # If running from tests/, tests are in ./
    
    current_dir = Path.cwd()
    if (current_dir / 'tests').exists():
        tests_dir = current_dir / 'tests'
        project_root = current_dir
    elif current_dir.name == 'tests':
        tests_dir = current_dir
        project_root = current_dir.parent
    else:
        # Fallback: assume script location is in tests/
        script_path = Path(__file__).resolve()
        tests_dir = script_path.parent
        project_root = tests_dir.parent

    print(f"🚀 Starting JUST CLI Test Suite (Worker Mode)")
    print(f"📂 Project Root: {project_root}")
    print(f"📂 Tests Dir: {tests_dir}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print("-" * 60)

    if not tests_dir.exists():
        print(f"❌ Tests directory not found: {tests_dir}")
        return False

    # Filter for test files, excluding this script and __init__.py
    test_files = sorted([
        f for f in tests_dir.glob('test_*.py') 
        if f.name != 'run_tests.py'
    ])
    
    # Also include manual_test_download.py if it exists (optional, maybe skip for automated?)
    # User renamed it to exclude from automated suite, so let's respect that or make it explicit.
    # For now, we stick to test_*.py pattern which is standard.

    if not test_files:
        print("⚠️  No tests found!")
        return False

    passed = 0
    failed = 0
    
    # Set PYTHONPATH to include src
    env = os.environ.copy()
    src_path = str(project_root / 'src')
    if 'PYTHONPATH' in env:
        env['PYTHONPATH'] = f"{src_path}{os.pathsep}{env['PYTHONPATH']}"
    else:
        env['PYTHONPATH'] = src_path

    for test_file in test_files:
        print(f"🏃 Running {test_file.name}...")
        try:
            # Run test file as a script
            result = subprocess.run(
                [sys.executable, str(test_file)],
                env=env,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"   ✅ PASS")
                passed += 1
            else:
                print(f"   ❌ FAIL")
                print(f"   Output:\n{result.stdout}")
                print(f"   Error:\n{result.stderr}")
                failed += 1
        except Exception as e:
            print(f"   💥 ERROR: {e}")
            failed += 1
        print("-" * 30)

    duration = time.time() - start_time
    print("-" * 60)
    
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print(f"✅ All tests passed in {duration:.2f}s")
        return True
    else:
        print(f"❌ Tests failed in {duration:.2f}s")
        return False

def run_docker_tests(project_root, proxy: str = ""):
    """Run tests inside Docker.
    
    Args:
        project_root: Path to the project root directory
        proxy: Optional proxy URL (e.g., http://proxy:port)
    """
    print("\n🐳 Running tests in Docker...")
    
    dockerfile_path = project_root / 'tests' / 'Dockerfile'
    if not dockerfile_path.exists():
        print(f"❌ Dockerfile not found at {dockerfile_path}")
        return False

    # Use command line proxy first, then fall back to environment variables
    if proxy:
        http_proxy = proxy
        https_proxy = proxy
    else:
        http_proxy = os.environ.get('HTTP_PROXY', os.environ.get('http_proxy', ''))
        https_proxy = os.environ.get('HTTPS_PROXY', os.environ.get('https_proxy', ''))
    
    if http_proxy or https_proxy:
        print(f"   Using proxy: HTTP={http_proxy or 'none'}, HTTPS={https_proxy or 'none'}")

    # Build image
    print("   Building Docker image...")
    build_cmd = [
        "docker", "build",
        "-t", "just-cli-test",
        "-f", str(dockerfile_path),
        "--build-arg", f"HTTP_PROXY={http_proxy}",
        "--build-arg", f"HTTPS_PROXY={https_proxy}",
        str(project_root)
    ]
    
    try:
        subprocess.run(build_cmd, check=True, capture_output=False)
    except subprocess.CalledProcessError:
        print("   ❌ Docker build failed")
        return False

    # Run container
    print("   Running tests in container...")
    run_cmd = [
        "docker", "run", "--rm",
        "just-cli-test"
    ]
    
    try:
        result = subprocess.run(run_cmd, check=False)
        if result.returncode == 0:
            print("   ✅ Docker tests passed")
            return True
        else:
            print("   ❌ Docker tests failed")
            return False
    except Exception as e:
        print(f"   💥 Error running Docker container: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="JUST CLI Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests (Docker + Local)
  python run_tests.py --proxy http://127.0.0.1:7890
  python run_tests.py --worker           # Run tests directly (no Docker)
"""
    )
    parser.add_argument(
        "--worker", 
        action="store_true", 
        help="Run in worker mode (execute tests directly, no Docker)"
    )
    parser.add_argument(
        "--proxy", "-p",
        type=str,
        default="http://host.docker.internal:7890",
        metavar="URL",
        help="Proxy URL for Docker build (e.g., http://host.docker.internal:7890)"
    )
    args = parser.parse_args()

    if args.worker:
        success = run_actual_tests()
        sys.exit(0 if success else 1)
    else:
        # Orchestrator Mode
        project_root = Path(__file__).resolve().parent.parent
        
        # 1. Run Docker Tests
        docker_success = run_docker_tests(project_root, proxy=args.proxy)
        
        # 2. Run Local Tests if Windows
        local_success = True
        if platform.system().lower() == "windows":
            print("\n🪟 Detected Windows, running local tests...")
            # Call self in worker mode
            cmd = [sys.executable, str(Path(__file__).resolve()), "--worker"]
            result = subprocess.run(cmd)
            local_success = (result.returncode == 0)
        
        # Final Result
        if not docker_success:
            print("\n❌ Docker tests failed!")
            sys.exit(1)
        
        if not local_success:
            print("\n❌ Local Windows tests failed!")
            sys.exit(1)
            
        print("\n✨ All tests passed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()
