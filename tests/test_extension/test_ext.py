import subprocess
import sys
from typing import List

from typing_extensions import Annotated
import typer

from just import create_typer_app
from . import docker_cli


build_cli = create_typer_app()
# Add the CLI to the parent CLI
docker_cli.add_typer(build_cli)


@build_cli.command(name="build")
def main(
    work_dir: Annotated[str, typer.Argument(
        help='',
        show_default=False
    )] = '.',
    tag: Annotated[str, typer.Option(
        '-t',
        help='',
        show_default=False
    )]
):
    command = r"""
    docker build --build-arg http_proxy=http://host.docker.internal:7890 --build-arg https_proxy=http://host.docker.internal:7890 -t TAG .
    """.strip()
    command = command.replace('.', str(work_dir))
    command = command.replace('TAG', str(tag))

    # Use shell=True for cross-platform compatibility (Windows shell built-ins like echo)
    subprocess.run(command, shell=True)
