#!/usr/bin/env python3
"""
Installer Container Test Runner
===============================
Runs installer tests with CLI support for single/multiple installers.
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

tests_dir = Path(__file__).parent.parent
sys.path.insert(0, str(tests_dir / "src"))
sys.path.insert(0, str(tests_dir))

from test_installers import (
    INSTALLER_CONFIGS,
    SKIPPED_INSTALLERS,
    run_single_installer_test,
)


def list_installers():
    print("📦 Available Installers:")
    print("=" * 40)
    for name in INSTALLER_CONFIGS:
        status = "⏭️  SKIPPED" if name in SKIPPED_INSTALLERS else "✅ Available"
        config = INSTALLER_CONFIGS[name]
        print(f"  {name:15} {status}")
        print(f"                  Verify: {config['verify_command']}")
    print()
    print(f"Total: {len(INSTALLER_CONFIGS)} installers")
    print(f"Skipped: {len(SKIPPED_INSTALLERS)} ({', '.join(SKIPPED_INSTALLERS)})")


def run_tests(installer_name=None, skip_list=None):
    skip_list = skip_list or []
    all_skipped = set(SKIPPED_INSTALLERS) | set(skip_list)

    if installer_name:
        if installer_name not in INSTALLER_CONFIGS:
            print(f"❌ Unknown installer: {installer_name}")
            print(f"   Available: {', '.join(INSTALLER_CONFIGS.keys())}")
            return False
        installers_to_test = [installer_name]
    else:
        installers_to_test = [
            name for name in INSTALLER_CONFIGS if name not in all_skipped
        ]

    print("🧪 Installer Container Integration Tests")
    print("=" * 50)
    print(f"Testing {len(installers_to_test)} installer(s)")
    if all_skipped:
        print(f"Skipping: {', '.join(all_skipped)}")
    print()

    passed = []
    failed = []
    skipped = list(all_skipped)
    start_time = time.time()

    for name in installers_to_test:
        if name in all_skipped:
            continue

        config = INSTALLER_CONFIGS[name]
        print(f"🏃 Testing {name}...")

        try:
            test_start = time.time()
            success = run_single_installer_test(name)
            elapsed = time.time() - test_start

            if success:
                print(f"   ✅ PASS ({config['verify_command']}) [{elapsed:.1f}s]")
                passed.append(name)
            else:
                print(f"   ❌ FAIL ({config['verify_command']}) [{elapsed:.1f}s]")
                failed.append(name)

        except subprocess.TimeoutExpired:
            print(f"   ⏱️  TIMEOUT (120s exceeded)")
            failed.append(name)
        except Exception as e:
            print(f"   💥 ERROR: {e}")
            failed.append(name)
        print()

    total_time = time.time() - start_time

    print("=" * 50)
    print(
        f"Results: {len(passed)} passed, {len(failed)} failed, {len(skipped)} skipped"
    )
    print(f"Total time: {total_time:.1f}s")

    if failed:
        print()
        print("❌ Failed installers:")
        for name in failed:
            print(f"   - {name}")

    return len(failed) == 0


def main():
    parser = argparse.ArgumentParser(description="Installer Container Test Runner")
    parser.add_argument(
        "--installer", "-i", type=str, metavar="NAME", help="Test a specific installer"
    )
    parser.add_argument(
        "--list", "-l", action="store_true", help="List all available installers"
    )
    parser.add_argument(
        "--skip",
        "-s",
        type=str,
        action="append",
        metavar="NAME",
        help="Skip specific installer",
    )

    args = parser.parse_args()

    if args.list:
        list_installers()
        return 0

    success = run_tests(installer_name=args.installer, skip_list=args.skip or [])
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
