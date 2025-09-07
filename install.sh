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

display_install_banner() {
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
    echo -e "${WHITE}                      INSTALLATION SCRIPT${NC}"
    echo -e "${CYAN}                         Version 2.0.0${NC}"
    echo "================================================================"
    echo
}

check_system() {
    echo -e "${CYAN}[INFO]${NC} Checking system compatibility..."
    
    if ! command -v apt &> /dev/null && ! command -v yum &> /dev/null && ! command -v pacman &> /dev/null; then
        echo -e "${RED}[ERROR]${NC} Unsupported package manager. This script supports apt, yum, and pacman."
        exit 1
    fi
    
    if [[ $EUID -eq 0 ]]; then
        echo -e "${YELLOW}[WARNING]${NC} Running as root. Some tools may not work correctly."
    fi
    
    echo -e "${GREEN}[OK]${NC} System compatibility verified"
}

install_tools() {
    echo -e "${CYAN}[INFO]${NC} Checking required tools..."
    
    local tools=(nmap masscan gobuster sqlmap whois nikto whatweb dig openssl curl wget git)
    local missing=()
    
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            missing+=("$tool")
        fi
    done
    
    if [ ${#missing[@]} -eq 0 ]; then
        echo -e "${GREEN}[OK]${NC} All required tools are already installed"
        return 0
    fi
    
    echo -e "${YELLOW}[INFO]${NC} Missing tools: ${missing[*]}"
    read -rp "Install missing tools? [Y/n]: " install_choice
    
    if [[ "$install_choice" =~ ^[Nn] ]]; then
        echo -e "${YELLOW}[WARNING]${NC} Some tools are missing. The scanner may not work correctly."
        return 0
    fi
    
    echo -e "${CYAN}[INFO]${NC} Installing missing tools..."
    
    if command -v apt &> /dev/null; then
        sudo apt update
        sudo apt install -y "${missing[@]}"
        
    elif command -v yum &> /dev/null; then
        sudo yum install -y "${missing[@]}"
        
    elif command -v pacman &> /dev/null; then
        sudo pacman -S --noconfirm "${missing[@]}"
    fi
    
    # Install Go tools if Go is available
    if command -v go &> /dev/null; then
        echo -e "${CYAN}[INFO]${NC} Installing Go-based tools..."
        
        if ! command -v subfinder &> /dev/null; then
            echo -e "${CYAN}[INFO]${NC} Installing subfinder..."
            go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
        fi
        
        if ! command -v nuclei &> /dev/null; then
            echo -e "${CYAN}[INFO]${NC} Installing nuclei..."
            go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest
        fi
        
        if ! command -v amass &> /dev/null; then
            echo -e "${CYAN}[INFO]${NC} Installing amass..."
            go install -v github.com/OWASP/Amass/v3/...@master
        fi
    else
        echo -e "${YELLOW}[WARNING]${NC} Go not found. Some tools (subfinder, nuclei, amass) will not be installed."
    fi
    
    echo -e "${GREEN}[OK]${NC} Tools installation completed"
}

download_wordlists() {
    echo -e "${CYAN}[INFO]${NC} Setting up wordlists..."
    
    local wordlist_dir="/usr/share/wordlists"
    
    if [ ! -d "$wordlist_dir" ]; then
        sudo mkdir -p "$wordlist_dir"
    fi
    
    # Ensure dirb wordlists exist
    if [ ! -d "$wordlist_dir/dirb" ]; then
        echo -e "${CYAN}[INFO]${NC} Setting up dirb wordlists..."
        sudo mkdir -p "$wordlist_dir/dirb"
        
        # Create basic wordlist if dirb package didn't install them
        if [ ! -f "$wordlist_dir/dirb/common.txt" ]; then
            echo -e "${CYAN}[INFO]${NC} Downloading common.txt..."
            sudo wget -q -O "$wordlist_dir/dirb/common.txt" "https://raw.githubusercontent.com/v0re/dirb/master/wordlists/common.txt" 2>/dev/null || echo "admin" | sudo tee "$wordlist_dir/dirb/common.txt" > /dev/null
        fi
        
        if [ ! -f "$wordlist_dir/dirb/big.txt" ]; then
            echo -e "${CYAN}[INFO]${NC} Downloading big.txt..."
            sudo wget -q -O "$wordlist_dir/dirb/big.txt" "https://raw.githubusercontent.com/v0re/dirb/master/wordlists/big.txt" 2>/dev/null || echo "admin" | sudo tee "$wordlist_dir/dirb/big.txt" > /dev/null
        fi
    fi
    
    echo -e "${GREEN}[OK]${NC} Wordlists setup completed"
}

install_nuclei_templates() {
    echo -e "${CYAN}[INFO]${NC} Setting up Nuclei templates..."
    
    if command -v nuclei &> /dev/null; then
        nuclei -update-templates &> /dev/null
        echo -e "${GREEN}[OK]${NC} Nuclei templates updated"
    else
        echo -e "${YELLOW}[WARNING]${NC} Nuclei not found, skipping template update"
    fi
}

install_scanner() {
    echo -e "${CYAN}[INFO]${NC} Installing Security Scanner..."
    
    # Download the main script
    curl -sSL https://raw.githubusercontent.com/mpgamer75/security-scanner/main/security -o security
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR]${NC} Failed to download scanner script"
        exit 1
    fi
    
    # Make executable
    chmod +x security
    
    # Install globally
    sudo mv security /usr/local/bin/
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[SUCCESS]${NC} Security Scanner installed successfully!"
        echo -e "${WHITE}You can now run:${NC} ${CYAN}security${NC}"
    else
        echo -e "${RED}[ERROR]${NC} Installation failed"
        exit 1
    fi
}

create_desktop_entry() {
    read -rp "Create desktop entry? [y/N]: " desktop_choice
    
    if [[ "$desktop_choice" =~ ^[Yy] ]]; then
        mkdir -p ~/.local/share/applications
        cat > ~/.local/share/applications/security-scanner.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Security Scanner
Comment=Advanced Security Assessment Tool
Exec=gnome-terminal -- security
Icon=utilities-system-monitor
Terminal=true
Categories=System;Security;
EOF
        echo -e "${GREEN}[OK]${NC} Desktop entry created"
    fi
}

main() {
    display_install_banner
    check_system
    install_tools
    download_wordlists
    install_nuclei_templates
    install_scanner
    create_desktop_entry
    
    echo
    echo "================================================================"
    echo -e "${GREEN}                     INSTALLATION COMPLETED${NC}"
    echo "================================================================"
    echo -e "${WHITE}Usage:${NC}"
    echo -e "  ${CYAN}security${NC}           # Start interactive scanner"
    echo -e "  ${CYAN}security --help${NC}    # Show help information"
    echo -e "  ${CYAN}security --version${NC} # Show version"
    echo
    echo -e "${YELLOW}Note: Use responsibly and only on systems you own or have permission to test${NC}"
    echo
}

# Execute main function
main "$@"