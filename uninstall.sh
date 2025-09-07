#!/bin/bash

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m'

display_uninstall_banner() {
    clear
    echo -e "${RED}"
    cat << "EOF"
    ███████╗███████╗ ██████╗██╗   ██╗██████╗ ██╗████████╗██╗   ██╗
    ██╔════╝██╔════╝██╔════╝██║   ██║██╔══██╗██║╚══██╔══╝╚██╗ ██╔╝
    ███████╗█████╗  ██║     ██║   ██║██████╔╝██║   ██║    ╚████╔╝ 
    ╚════██║██╔══╝  ██║     ██║   ██║██╔══██╗██║   ██║     ╚██╔╝  
    ███████║███████╗╚██████╗╚██████╔╝██║  ██║██║   ██║      ██║   
    ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝   ╚═╝      ╚═╝   
                                                                   
    ███████╗ ██████╗ █████╗ ███╗   ██╗███╗   ██╗███████╗██████╗ 
    ██╔════╝██╔════╝██╔══██╗████╗  ██║████╗  ██║██╔════╝██╔══██╗
    ███████╗██║     ███████║██╔██╗ ██║██╔██╗ ██║█████╗  ██████╔╝
    ╚════██║██║     ██╔══██║██║╚██╗██║██║╚██╗██║██╔══╝  ██╔══██╗
    ███████║╚██████╗██║  ██║██║ ╚████║██║ ╚████║███████╗██║  ██║
    ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝
EOF
    echo -e "${NC}"
    echo "================================================================"
    echo -e "${WHITE}                    UNINSTALLATION SCRIPT${NC}"
    echo -e "${CYAN}                         Version 2.0.0${NC}"
    echo "================================================================"
    echo
}

confirm_uninstall() {
    echo -e "${YELLOW}[WARNING]${NC} This will completely remove Security Scanner and its components."
    echo -e "${WHITE}The following will be removed:${NC}"
    echo "  - Security Scanner executable (/usr/local/bin/security)"
    echo "  - Desktop entry (~/.local/share/applications/security-scanner.desktop)"
    echo "  - Configuration files (if any)"
    echo
    echo -e "${RED}Note: Scan results and wordlists will NOT be removed.${NC}"
    echo
    
    read -rp "Are you sure you want to uninstall Security Scanner? [y/N]: " confirm
    
    if [[ ! "$confirm" =~ ^[Yy] ]]; then
        echo -e "${CYAN}[INFO]${NC} Uninstallation cancelled by user."
        exit 0
    fi
}

remove_executable() {
    echo -e "${CYAN}[INFO]${NC} Removing Security Scanner executable..."
    
    if [ -f "/usr/local/bin/security" ]; then
        sudo rm -f /usr/local/bin/security
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}[OK]${NC} Executable removed from /usr/local/bin/security"
        else
            echo -e "${RED}[ERROR]${NC} Failed to remove executable"
            return 1
        fi
    else
        echo -e "${YELLOW}[INFO]${NC} Executable not found in /usr/local/bin/"
    fi
}

remove_desktop_entry() {
    echo -e "${CYAN}[INFO]${NC} Removing desktop entry..."
    
    if [ -f "$HOME/.local/share/applications/security-scanner.desktop" ]; then
        rm -f "$HOME/.local/share/applications/security-scanner.desktop"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}[OK]${NC} Desktop entry removed"
        else
            echo -e "${RED}[ERROR]${NC} Failed to remove desktop entry"
        fi
    else
        echo -e "${YELLOW}[INFO]${NC} Desktop entry not found"
    fi
}

remove_go_tools() {
    echo -e "${CYAN}[INFO]${NC} Checking for Go-based security tools..."
    
    local go_tools=("subfinder" "nuclei" "amass" "assetfinder")
    local removed_tools=()
    
    read -rp "Remove Go-based security tools (subfinder, nuclei, amass)? [y/N]: " remove_go
    
    if [[ "$remove_go" =~ ^[Yy] ]]; then
        if command -v go &> /dev/null; then
            local gopath=$(go env GOPATH)
            
            for tool in "${go_tools[@]}"; do
                if [ -f "$gopath/bin/$tool" ]; then
                    rm -f "$gopath/bin/$tool"
                    removed_tools+=("$tool")
                    echo -e "${GREEN}[OK]${NC} Removed $tool"
                fi
            done
            
            if [ ${#removed_tools[@]} -gt 0 ]; then
                echo -e "${GREEN}[OK]${NC} Removed Go tools: ${removed_tools[*]}"
            else
                echo -e "${YELLOW}[INFO]${NC} No Go tools found to remove"
            fi
        else
            echo -e "${YELLOW}[INFO]${NC} Go not found, skipping Go tools removal"
        fi
    else
        echo -e "${YELLOW}[SKIP]${NC} Go tools removal skipped by user"
    fi
}

clean_scan_results() {
    echo -e "${CYAN}[INFO]${NC} Checking for scan results..."
    
    local scan_dirs=($(find . -maxdepth 1 -name "security_scan_*" -type d 2>/dev/null))
    
    if [ ${#scan_dirs[@]} -gt 0 ]; then
        echo -e "${YELLOW}[FOUND]${NC} Found ${#scan_dirs[@]} scan result directories:"
        for dir in "${scan_dirs[@]}"; do
            echo "  - $dir"
        done
        
        read -rp "Remove all scan result directories? [y/N]: " remove_scans
        
        if [[ "$remove_scans" =~ ^[Yy] ]]; then
            for dir in "${scan_dirs[@]}"; do
                rm -rf "$dir"
                echo -e "${GREEN}[OK]${NC} Removed $dir"
            done
        else
            echo -e "${YELLOW}[SKIP]${NC} Scan results preserved"
        fi
    else
        echo -e "${YELLOW}[INFO]${NC} No scan result directories found"
    fi
}

remove_config_files() {
    echo -e "${CYAN}[INFO]${NC} Checking for configuration files..."
    
    local config_files=(
        "$HOME/.security-scanner"
        "$HOME/.config/security-scanner"
        "/etc/security-scanner"
    )
    
    local found_configs=()
    
    for config in "${config_files[@]}"; do
        if [ -e "$config" ]; then
            found_configs+=("$config")
        fi
    done
    
    if [ ${#found_configs[@]} -gt 0 ]; then
        echo -e "${YELLOW}[FOUND]${NC} Found configuration files:"
        for config in "${found_configs[@]}"; do
            echo "  - $config"
        done
        
        read -rp "Remove configuration files? [y/N]: " remove_configs
        
        if [[ "$remove_configs" =~ ^[Yy] ]]; then
            for config in "${found_configs[@]}"; do
                if [[ "$config" == "/etc/security-scanner" ]]; then
                    sudo rm -rf "$config"
                else
                    rm -rf "$config"
                fi
                echo -e "${GREEN}[OK]${NC} Removed $config"
            done
        else
            echo -e "${YELLOW}[SKIP]${NC} Configuration files preserved"
        fi
    else
        echo -e "${YELLOW}[INFO]${NC} No configuration files found"
    fi
}

show_reinstall_info() {
    echo -e "\n${CYAN}[INFO]${NC} To reinstall Security Scanner, use:"
    echo -e "${WHITE}curl -sSL https://raw.githubusercontent.com/mpgamer75/security-scanner/main/install.sh | bash${NC}"
    echo
    echo -e "${YELLOW}Or for manual installation:${NC}"
    echo -e "${WHITE}git clone https://github.com/mpgamer75/security-scanner.git${NC}"
    echo -e "${WHITE}cd security-scanner && chmod +x install.sh && ./install.sh${NC}"
}

main() {
    display_uninstall_banner
    confirm_uninstall
    
    echo -e "${CYAN}[INFO]${NC} Starting Security Scanner uninstallation..."
    echo
    
    remove_executable
    remove_desktop_entry
    remove_go_tools
    clean_scan_results
    remove_config_files
    
    echo
    echo "================================================================"
    echo -e "${GREEN}                   UNINSTALLATION COMPLETED${NC}"
    echo "================================================================"
    echo -e "${GREEN}[SUCCESS]${NC} Security Scanner has been removed from your system"
    
    show_reinstall_info
    
    echo -e "${YELLOW}Thank you for using Security Scanner!${NC}"
    echo
}

# Execute main function
main "$@"