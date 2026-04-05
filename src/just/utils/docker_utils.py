"""Docker容器工具类"""

import subprocess
from typing import Dict, Optional, Tuple


class DockerContainer:
    """Docker容器上下文管理器

    用法:
        # 基本用法
        with DockerContainer(image="ubuntu:latest") as container:
            exit_code, output = container.exec_command("ls /")

        # 带环境变量
        with DockerContainer(
            image="ubuntu:latest",
            envs={"HTTP_PROXY": "http://127.0.0.1:7890"}
        ) as container:
            exit_code, output = container.exec_command("env | grep proxy")

        # 指定容器名称
        with DockerContainer(
            image="ubuntu:latest",
            name="my-test-container"
        ) as container:
            pass
    """

    def __init__(
        self,
        image: str,
        name: Optional[str] = None,
        envs: Optional[Dict[str, str]] = None
    ):
        """初始化容器管理器

        Args:
            image: Docker镜像名称
            name: 容器名称（可选）
            envs: 环境变量字典（可选）
        """
        self.image = image
        self.name = name
        self.envs = envs or {}
        self.container_id = None

    def __enter__(self):
        """启动容器并返回self"""
        cmd = ["docker", "run", "-d", "--rm"]

        # 添加容器名称
        if self.name:
            cmd.extend(["--name", self.name])

        # 添加环境变量
        for key, value in self.envs.items():
            cmd.extend(["-e", f"{key}={value}"])

        # 镜像和启动命令
        cmd.extend([self.image, "tail", "-f", "/dev/null"])

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to start container: {result.stderr}")

        self.container_id = result.stdout.strip()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """停止并删除容器"""
        if self.container_id:
            stop_cmd = ["docker", "stop"]
            if self.name:
                stop_cmd.append(self.name)
            else:
                stop_cmd.append(self.container_id)

            subprocess.run(stop_cmd, capture_output=True, timeout=30)
            self.container_id = None

    def exec_command(
        self,
        command: str,
        capture_output: bool = False,
        interactive: bool = True
    ) -> Tuple[int, str]:
        """在容器内执行命令

        Args:
            command: 要执行的命令
            capture_output: 是否捕获输出
            interactive: 是否使用交互模式(TTY)

        Returns:
            Tuple[int, str]: (exit_code, output)
        """
        cmd = ["docker", "exec"]
        if interactive:
            cmd.extend(["-it"])

        # 添加环境变量（确保 PATH 正确设置）
        for key, value in self.envs.items():
            cmd.extend(["-e", f"{key}={value}"])

        # 使用容器名称或ID
        target = self.name or self.container_id
        cmd.append(target)
        cmd.extend(command.split())

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
