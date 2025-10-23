import os
from just import just_cli, capture_exception, echo


@just_cli.command(name="tunnel", help="Create Cloudflare tunnel.")
@capture_exception
def create_cloudflare_tunnel(url: str):
    cmd = f"cloudflared tunnel --url {url}"
    echo.echo("> {cmd}")
    os.system(cmd)
