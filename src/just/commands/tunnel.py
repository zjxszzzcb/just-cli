import shlex
import subprocess
import typer

from typing_extensions import Annotated

from just import create_typer_app, capture_exception, echo

from just.extensions import just_cli


tunnel_cli = create_typer_app()

@just_cli.command(name="tunnel", help="Create Cloudflare tunnel.")
@capture_exception
def create_cloudflare_tunnel(
    url: Annotated[str, typer.Argument(
        help='',
        show_default=False
    )]
 ):
    command = r"""
    cloudflared tunnel --url <URL>
    """
    command = command.replace('<URL>', url)
    subprocess.run(shlex.split(command), shell=True)
