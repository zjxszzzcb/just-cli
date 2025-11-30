import just

@just.installer(check="cloudflared --version")
def install_cloudflare():
    """
    Install Cloudflare Tunnel client (cloudflared).
    """
    if just.system.pms.winget.is_available():
        just.execute_commands("winget install --id Cloudflare.cloudflared")
    elif just.system.pms.brew.is_available():
        just.execute_commands("brew install cloudflared")
    elif just.system.platform == 'linux' and just.system.arch == 'x86_64':
        url = 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64'
        just.BinaryInstaller(url, alias='cloudflared').run()
    else:
        raise NotImplementedError
