import os
from just import create_typer_app, echo, just_cli

cloudflared_cli = create_typer_app(name="cloudflared", help="Cloudflare toolkit.")
tunnel_cli = create_typer_app(name="tunnel", help="Cloudflare tunnel toolkit.")
cloudflared_cli.add_typer(tunnel_cli)
just_cli.add_typer(cloudflared_cli)


@cloudflared_cli.command(name="readme", help="Read Cloudflare toolkit readme.")
def readme():
    echo.markdown(
        r"""
        ## Install Cloudflare
    
        ### Windows
    
        ```powershell
        winget install --id Cloudflare.cloudflared
        ```
    
    
        ### Debian and Ubuntu APT
    
        ```bash
        # 1. Add Cloudflare's package signing key:
        sudo mkdir -p --mode=0755 /usr/share/keyrings
        curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | \
            sudo tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null
        # 2. Add Cloudflare's apt repo to your apt repositories:
        echo "deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared any main" \
            | sudo tee /etc/apt/sources.list.d/cloudflared.list
        # 3. Update apt and install cloudflared:
        sudo apt-get update && sudo apt-get install cloudflared
        ```
    
    
        ### Other
    
        Referer to https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/\
        do-more-with-tunnels/local-management/create-local-tunnel/
    
    
        ## Cloudflare Usage
    
        ### Authenticate cloudflared
    
        ```bash
        cloudflared tunnel login
        ```
    
    
        ### Start tunnel
        ```
        cloudflared tunnel --url http://localhost:8000
        ```
        """
    )


@tunnel_cli.command(name="login", help="Login Cloudflare toolkit.")
def tunnel_login():
    cmd = "cloudflared tunnel login"
    echo.echo("> {cmd}")
    os.system(cmd)
