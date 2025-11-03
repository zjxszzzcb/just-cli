import typer

from typing_extensions import Annotated

from just import create_typer_app, capture_exception, just_cli
from just.utils import execute_command


tunnel_cli = create_typer_app()


@just_cli.command(name="tunnel")
@capture_exception
def create_cloudflare_tunnel(
    url: Annotated[str, typer.Argument(
        help='The URL to tunnel',
        show_default=False
    )]
):
    """
    Create Cloudflare tunnel.
    """
    command = r"""
    cloudflared tunnel --url <URL>
    """
    command = command.replace('<URL>', url)
    execute_command(command)
