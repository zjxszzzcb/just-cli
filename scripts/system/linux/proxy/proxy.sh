#!/bin/bash

# Proxy Control Functions
# Source this file to use: source proxy.sh
# Or install to ~/.bashrc for permanent availability

# Set proxy variables from environment or use default
HTTP_PROXY_URL=${HTTP_PROXY_URL:-"http://127.0.0.1:7890"}
HTTPS_PROXY_URL=${HTTPS_PROXY_URL:-$HTTP_PROXY_URL}

# Proxy control function
proxy() {
    case "${1,,}" in
        on)
            export HTTP_PROXY=$HTTP_PROXY_URL
            export HTTPS_PROXY=$HTTPS_PROXY_URL
            export http_proxy=$HTTP_PROXY_URL
            export https_proxy=$HTTPS_PROXY_URL
            echo -e "\033[32m[ON]\033[0m HTTP  Proxy $HTTP_PROXY enabled in Bash"
            echo -e "\033[32m[ON]\033[0m HTTPS Proxy $HTTPS_PROXY enabled in Bash"
            ;;
        off)
            if [[ -n "$HTTP_PROXY" ]]; then
                echo -e "\033[31m[OFF]\033[0m HTTP  Proxy $HTTP_PROXY disabled in Bash"
                echo -e "\033[31m[OFF]\033[0m HTTPS Proxy $HTTPS_PROXY disabled in Bash"
            else
                echo -e "\033[31m[OFF]\033[0m Proxy disabled in Bash"
            fi
            unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy
            ;;
        uninstall)
            uninstall_proxy
            ;;
        -h|h|help|"")
            echo
            echo "Proxy Control Function"
            echo "=========================================="
            echo "Usage:"
            echo "  proxy on         - Enable proxy"
            echo "  proxy off        - Disable proxy"
            echo "  proxy uninstall  - Uninstall CLI"
            echo
            echo "Current HTTP_PROXY : $HTTP_PROXY_URL"
            echo "Current HTTPS_PROXY: $HTTPS_PROXY_URL"
            echo "=========================================="
            ;;
        install)
            echo -e "\033[31m[ERROR]\033[0m Use 'bash proxy.sh install' instead"
            ;;
        *)
            echo "Invalid argument: $1"
            echo
            echo "Usage: proxy [on|off|uninstall|-h]"
            ;;
    esac
}

install_proxy() {
    local bashrc="$HOME/.bashrc"

    # Get absolute path in a more compatible way
    local script_path="$0"
    if [[ "$script_path" != /* ]]; then
        script_path="$(pwd)/$script_path"
    fi

    # Normalize path to remove ./ components
    script_path="${script_path//\/.\//\/}"

    # Check if already installed
    if grep -q "# Proxy Control Functions - Installed by proxy.sh" "$bashrc" 2>/dev/null; then
        echo -e "\033[33m[WARN]\033[0m Proxy already installed in $bashrc"
        return 1
    fi

    # Add installation marker and source command
    echo "" >> "$bashrc"
    echo "# Proxy Control Functions - Installed by proxy.sh" >> "$bashrc"
    echo "source \"$script_path\"" >> "$bashrc"
    echo "# End of Proxy Control Functions" >> "$bashrc"

    echo -e "\033[32m[OK]\033[0m Proxy installed to $bashrc"
    echo "Restart your terminal or run: source ~/.bashrc"
}

uninstall_proxy() {
    local bashrc="$HOME/.bashrc"

    # Check if installed
    if ! grep -q "# Proxy Control Functions - Installed by proxy.sh" "$bashrc" 2>/dev/null; then
        echo -e "\033[33m[WARN]\033[0m Proxy not found in $bashrc"
        return 1
    fi

    # Remove installation
    sed -i '/# Proxy Control Functions - Installed by proxy.sh/,/# End of Proxy Control Functions/d' "$bashrc"

    echo -e "\033[32m[OK]\033[0m Proxy uninstalled from $bashrc"
    echo "Restart your terminal or run: source ~/.bashrc"
}

# Show help when script is executed without arguments
show_script_help() {
    echo
    echo "Proxy Control Script"
    echo "=========================================="
    echo "Usage:"
    echo "  bash proxy.sh install    - Install CLI"
    echo "  bash proxy.sh uninstall  - Uninstall CLI"
    echo
    echo "Current HTTP_PROXY : $HTTP_PROXY_URL"
    echo "Current HTTPS_PROXY: $HTTPS_PROXY_URL"
    echo "=========================================="
}

# Main execution logic
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Script is being executed directly
    case "${1,,}" in
        install)
            install_proxy
            ;;
        uninstall)
            uninstall_proxy
            ;;
        -h|h|help|"")
            show_script_help
            ;;
        *)
            proxy "$@"
            ;;
    esac
else
    # Script is being sourced
    # Only define the proxy function, not install/uninstall
    :
fi