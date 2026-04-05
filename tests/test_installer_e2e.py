#!/usr/bin/env python3
"""Installer E2E Tests"""

import argparse
import subprocess
import sys
import uuid

from loguru import logger

from just.core.installer.install_package import list_available_installers
from just.utils.shell_utils import execute_command
from just.utils.docker_utils import DockerContainer


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Just Installer E2E Tests")
    parser.add_argument(
        "installers",
        nargs="*",
        help="Specific installer names to test. If not provided, test all installers"
    )
    parser.add_argument(
        "--proxy",
        type=str,
        help="Proxy URL for downloads (e.g., http://127.0.0.1:7890)"
    )
    parser.add_argument(
        "--image",
        type=str,
        default=None,
        help="Docker image to use for testing. If not provided, tests run on local machine"
    )
    return parser.parse_args()


def test_installer(name: str, proxy: str = None, container: DockerContainer = None) -> bool:
    """Test a single installer on local machine or in container.

    Args:
        name: Installer name
        proxy: Optional proxy URL
        container: Optional DockerContainer instance for container testing

    Returns:
        True if installation succeeded, False otherwise
    """
    logger.info(f"Testing `{name}` installer ...")

    cmd = f"just install {name}"
    if proxy:
        cmd += f" --proxy {proxy}"

    logger.info('-'*60)
    # Execute command based on context
    if container:
        exit_code, _ = container.exec_command(cmd)
    else:
        exit_code, _ = execute_command(cmd, capture_output=True)
    logger.info('-'*60)

    if exit_code == 0:
        logger.success("Installed successfully")
        return True
    else:
        logger.error("Installation failed")
        return False


def main():
    args = parse_args()
    passed = []
    failed = []

    # Get available installers
    installers = list_available_installers()

    # Determine which installers to test
    if args.installers:
        # User specified specific installers
        installer_names = args.installers
    else:
        # Test all installers
        installer_names = [inst['name'] for inst in installers]

    logger.info("🐳 Just Installer E2E Tests")
    logger.info("=" * 60)

    if args.image:
        # Container mode
        logger.info(f"Testing in container with image: {args.image}")

        # Prepare environment variables
        envs = {
            'PATH': '/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/root/.just/bin'
        }
        if args.proxy:
            envs.update({
                'HTTP_PROXY': args.proxy,
                'HTTPS_PROXY': args.proxy,
                'http_proxy': args.proxy,
                'https_proxy': args.proxy,
            })

        container_name = f"just-e2e-{uuid.uuid4().hex[:8]}"
        with DockerContainer(image=args.image, name=container_name, envs=envs) as container:
            logger.success(f"Container started: {container_name}\n")

            for name in installer_names:
                if test_installer(name, args.proxy, container):
                    passed.append(name)
                else:
                    failed.append(name)

            # Interactive container entry
            logger.info("=" * 60)
            user_input = input("Enter container for debugging? [y/N]: ")
            if user_input.lower() == 'y':
                subprocess.run(["docker", "exec", "-it", container_name, "bash"])
    else:
        # Local machine mode
        logger.info(f"Testing on local machine")

        for name in installer_names:
            if test_installer(name, args.proxy):
                passed.append(name)
            else:
                failed.append(name)

    logger.info("=" * 60)
    logger.info(f"Results: {len(passed)} passed, {len(failed)} failed")

    if failed:
        logger.error(f"Failed: {', '.join(failed)}")

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
