# Parse command line arguments manually to handle -h properly
$Action = $args[0]

# Set proxy variables from environment or use default
$HTTP_PROXY_URL = if ($env:HTTP_PROXY_URL) { $env:HTTP_PROXY_URL } else { "http://127.0.0.1:7890" }
$HTTPS_PROXY_URL = if ($env:HTTPS_PROXY_URL) { $env:HTTPS_PROXY_URL } else { $HTTP_PROXY_URL }

function Show-Help {
    Write-Host ""
    Write-Host "Proxy Control Script"
    Write-Host "=========================================="
    Write-Host "Usage:"
    Write-Host "  proxy.ps1 on     - Enable proxy"
    Write-Host "  proxy.ps1 off    - Disable proxy"
    Write-Host ""
    Write-Host "Current HTTP_PROXY : $HTTP_PROXY_URL"
    Write-Host "Current HTTPS_PROXY: $HTTPS_PROXY_URL"
    Write-Host "=========================================="
}

function Enable-Proxy {
    $env:HTTP_PROXY = $HTTP_PROXY_URL
    $env:HTTPS_PROXY = $HTTPS_PROXY_URL
    Write-Host "[ON]" -ForegroundColor Green -NoNewline
    Write-Host " HTTP  Proxy $env:HTTP_PROXY enabled in PowerShell"
    Write-Host "[ON]" -ForegroundColor Green -NoNewline
    Write-Host " HTTPS Proxy $env:HTTPS_PROXY enabled in PowerShell"
}

function Disable-Proxy {
    $currentProxy = $env:HTTP_PROXY
    if ($currentProxy) {
        Write-Host "[OFF]" -ForegroundColor Red -NoNewline
        Write-Host " HTTP  Proxy $env:HTTP_PROXY disabled in PowerShell"
        Write-Host "[OFF]" -ForegroundColor Red -NoNewline
        Write-Host " HTTPS Proxy $env:HTTPS_PROXY disabled in PowerShell"
    } else {
        Write-Host "[OFF]" -ForegroundColor Red -NoNewline
        Write-Host " Proxy disabled in PowerShell"
    }
    Remove-Item Env:HTTP_PROXY -ErrorAction SilentlyContinue
    Remove-Item Env:HTTPS_PROXY -ErrorAction SilentlyContinue
}

# Main logic
if (-not $Action -or $Action -eq "" -or $Action -eq "-h" -or $Action -eq "h" -or $Action -eq "help") {
    Show-Help
} else {
    switch ($Action) {
        "on" { Enable-Proxy }
        "off" { Disable-Proxy }
        default {
            Write-Host "Invalid argument: $Action"
            Write-Host ""
            Show-Help
        }
    }
}