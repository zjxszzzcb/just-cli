#!/bin/zsh

# Proxy Control Functions
# Source this file to use: source proxy.sh
# Or install to ~/.zshrc for permanent availability

# Set proxy variables from environment or use default
HTTP_PROXY_URL=${HTTP_PROXY_URL:-"http://127.0.0.1:7890"}
HTTPS_PROXY_URL=${HTTPS_PROXY_URL:-$HTTP_PROXY_URL}

# Proxy control function
proxy() {
    local cmd="${(L)1}"
    case "$cmd" in
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
            echo -e "\033[31m[ERROR]\033[0m Use 'zsh proxy.sh install' instead"
            ;;
        *)
            echo "Invalid argument: $1"
            echo
            echo "Usage: proxy [on|off|uninstall|-h]"
            ;;
    esac
}

install_proxy() {
    local zshrc="$HOME/.zshrc"

    # Get absolute path - zsh uses $0 for sourced script path
    local script_path="${0:A}"
    if [[ ! -f "$script_path" ]]; then
        script_path="$(pwd)/proxy.sh"
    fi

    # Check if already installed
    if grep -q "# Proxy Control Functions - Installed by proxy.sh" "$zshrc" 2>/dev/null; then
        echo -e "\033[33m[WARN]\033[0m Proxy already installed in $zshrc"
        return 1
    fi

    # Add installation marker and source command
    echo "" >> "$zshrc"
    echo "# Proxy Control Functions - Installed by proxy.sh" >> "$zshrc"
    echo "source \"$script_path\"" >> "$zshrc"
    echo "# End of Proxy Control Functions" >> "$zshrc"

    echo -e "\033[32m[OK]\033[0m Proxy installed to $zshrc"
    echo "Restart your terminal or run: source ~/.zshrc"
}

uninstall_proxy() {
    local zshrc="$HOME/.zshrc"

    # Check if installed
    if ! grep -q "# Proxy Control Functions - Installed by proxy.sh" "$zshrc" 2>/dev/null; then
        echo -e "\033[33m[WARN]\033[0m Proxy not found in $zshrc"
        return 1
    fi

    # Remove installation
    sed -i '' '/# Proxy Control Functions - Installed by proxy.sh/,/# End of Proxy Control Functions/d' "$zshrc"

    echo -e "\033[32m[OK]\033[0m Proxy uninstalled from $zshrc"
    echo "Restart your terminal or run: source ~/.zshrc"
}

# Show help when script is executed without arguments
show_script_help() {
    echo
    echo "Proxy Control Script"
    echo "=========================================="
    echo "Usage:"
    echo "  zsh proxy.sh install    - Install CLI"
    echo "  zsh proxy.sh uninstall  - Uninstall CLI"
    echo
    echo "Current HTTP_PROXY : $HTTP_PROXY_URL"
    echo "Current HTTPS_PROXY: $HTTPS_PROXY_URL"
    echo "=========================================="
}

# Main execution logic
# Check if script is being sourced or executed directly
# Direct exec: ZSH_EVAL_CONTEXT=toplevel (no 'file')
# Sourced in .zshrc: ZSH_EVAL_CONTEXT=toplevel:file (contains 'file')
if [[ "$ZSH_EVAL_CONTEXT" != *file* ]]; then
    # Script is being executed directly
    local cmd="${(L)1}"
    case "$cmd" in
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
fi
# When sourced (ZSH_EVAL_CONTEXT contains 'file'), only define functions
