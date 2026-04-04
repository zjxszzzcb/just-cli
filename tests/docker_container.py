"""Docker容器上下文管理器 - 用于E2E测试

该模块提供了一个简单的Docker容器上下文管理器,用于在容器内执行命令测试installer。
设计类似shell_utils的execute_command接口,支持with语句自动管理容器生命周期。
"""

import subprocess
import uuid
from typing import Tuple


class DockerContainer:
    """Docker容器上下文管理器

    用法:
        with DockerContainer() as container:
            exit_code, output = container.exec_command("just install cloudflare")
            exit_code, version = container.exec_command("cloudflared --version")
    """

    def __init__(self, image_name: str = "just:latest", name: str = None):
        """初始化容器管理器

        Args:
            image_name: Docker镜像名称,默认为 "just:latest"
            name: 容器名称,默认自动生成
        """
        self.image_name = image_name
        self.container_name = name or f"just-e2e-{uuid.uuid4().hex[:8]}"
        self.container_id = None

    def __enter__(self):
        """启动容器并返回self"""
        cmd = [
            "docker", "run", "-d",
            "--name", self.container_name,
            "--rm",
            "-e", "PATH=/usr/local/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin:/root/.just/bin:/root/.local/bin",
            self.image_name,
            "tail", "-f", "/dev/null"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to start container: {result.stderr}")
        self.container_id = result.stdout.strip()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """停止并删除容器"""
        if self.container_id:
            subprocess.run(
                ["docker", "stop", self.container_name],
                capture_output=True,
                timeout=30
            )
            self.container_id = None

    def exec_command(self, command: str, capture_output: bool = False, interactive: bool = True) -> Tuple[int, str]:
        """在容器内执行命令

        Args:
            command: 要执行的命令
            capture_output: 是否捕获输出,默认为True
            interactive: 是否使用交互模式(TTY),默认为False

        Returns:
            Tuple[int, str]: (exit_code, output)
            output包含stdout,如果失败则包含stderr信息
        """
        # Build docker exec command
        cmd = ["docker", "exec"]
        if interactive:
            cmd.extend(["-it"])
        cmd.append(self.container_name)
        cmd.extend(command.split())


        # Run command
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            timeout=120,
            stdin=subprocess.DEVNULL if not interactive else None
        )

        output = result.stdout
        if result.returncode != 0:
            output = result.stderr or result.stdout

        return result.returncode, output
