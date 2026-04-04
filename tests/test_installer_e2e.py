#!/usr/bin/env python3
"""Installer E2E Tests"""

import sys
from pathlib import Path

tests_dir = Path(__file__).parent
sys.path.insert(0, str(tests_dir))

from docker_container import DockerContainer
from container_installers.test_installers import INSTALLER_CONFIGS


def main():
    passed = []
    failed = []

    print("🐳 Installer E2E Tests")
    print("=" * 60)

    with DockerContainer() as container:
        print(f"✅ Container started: {container.container_name}\n")

        for name, config in INSTALLER_CONFIGS.items():
            print(f"📦 Testing {name}...")

            # Install
            exit_code, output = container.exec_command(f"just install {name}")
            if exit_code != 0:
                print(f"   ❌ {output[:100]}")
                failed.append(name)
                print()
                continue

            # Verify
            verify_cmd = config["verify_command"]
            exit_code, output = container.exec_command(verify_cmd)
            if exit_code == 0:
                version = output.strip().split('\n')[0]
                print(f"   ✅ {version}")
                passed.append(name)
            else:
                print(f"   ❌ {output[:100]}")
                failed.append(name)

            print()

    print("=" * 60)
    print(f"Results: {len(passed)} passed, {len(failed)} failed")

    if failed:
        print(f"\n❌ Failed: {', '.join(failed)}")

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
