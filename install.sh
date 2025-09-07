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
    
    if ! command -v curl &> /dev/null; then
        echo -e "${RED}[ERROR]${NC} curl is required but not installed."
        exit 1
    fi
    
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

download_wordlist() {
    local url="$1"
    local output="$2"
    local use_sudo="$3"
    
    if [ "$use_sudo" = true ]; then
        curl -sSL --connect-timeout 10 --max-time 60 "$url" | sudo tee "$output" > /dev/null 2>&1
    else
        curl -sSL --connect-timeout 10 --max-time 60 "$url" -o "$output" 2>/dev/null
    fi
    
    return $?
}

install_wordlists() {
    echo -e "${CYAN}[INFO]${NC} Setting up wordlists..."
    
    local wordlist_dir="/usr/share/wordlists/dirb"
    local use_sudo=true
    
    # Vérifie si on peut écrire dans /usr/share/wordlists
    if [ ! -d "$wordlist_dir" ]; then
        if ! sudo mkdir -p "$wordlist_dir" 2>/dev/null; then
            wordlist_dir="$HOME/.local/share/wordlists/dirb"
            mkdir -p "$wordlist_dir"
            use_sudo=false
            echo -e "${YELLOW}[INFO]${NC} Using local wordlist directory: $wordlist_dir"
        fi
    fi
    
    # Vérifie si les wordlists existent déjà
    if [ -f "$wordlist_dir/common.txt" ] && [ -f "$wordlist_dir/big.txt" ]; then
        local common_size=$(stat -c%s "$wordlist_dir/common.txt" 2>/dev/null || stat -f%z "$wordlist_dir/common.txt" 2>/dev/null || echo "0")
        local big_size=$(stat -c%s "$wordlist_dir/big.txt" 2>/dev/null || stat -f%z "$wordlist_dir/big.txt" 2>/dev/null || echo "0")
        
        if [ "$common_size" -gt 1000 ] && [ "$big_size" -gt 5000 ]; then
            echo -e "${GREEN}[OK]${NC} Wordlists already available"
            return 0
        fi
    fi
    
    read -rp "Download and install wordlists for web scanning? [Y/n]: " install_choice
    
    if [[ "$install_choice" =~ ^[Nn] ]]; then
        echo -e "${YELLOW}[SKIP]${NC} Wordlists installation skipped"
        return 0
    fi
    
    echo -e "${CYAN}[INFO]${NC} Downloading wordlists..."
    
    # Sources de wordlists (ordre de préférence)
    local common_sources=(
        "https://raw.githubusercontent.com/v0re/dirb/master/wordlists/common.txt"
        "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt"
        "https://raw.githubusercontent.com/maurosoria/dirsearch/master/db/dicc.txt"
    )
    
    local big_sources=(
        "https://raw.githubusercontent.com/v0re/dirb/master/wordlists/big.txt"
        "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/big.txt"
        "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/directory-list-2.3-medium.txt"
    )
    
    # Télécharge common.txt
    local downloaded=false
    for url in "${common_sources[@]}"; do
        echo -e "${CYAN}[INFO]${NC} Trying to download common.txt from $(echo $url | cut -d'/' -f3)..."
        if download_wordlist "$url" "$wordlist_dir/common.txt" "$use_sudo"; then
            echo -e "${GREEN}[OK]${NC} Downloaded common.txt"
            downloaded=true
            break
        fi
    done
    
    if [ "$downloaded" = false ]; then
        echo -e "${YELLOW}[FALLBACK]${NC} Creating minimal common.txt"
        create_minimal_common "$wordlist_dir/common.txt" "$use_sudo"
    fi
    
    # Télécharge big.txt
    downloaded=false
    for url in "${big_sources[@]}"; do
        echo -e "${CYAN}[INFO]${NC} Trying to download big.txt from $(echo $url | cut -d'/' -f3)..."
        if download_wordlist "$url" "$wordlist_dir/big.txt" "$use_sudo"; then
            echo -e "${GREEN}[OK]${NC} Downloaded big.txt"
            downloaded=true
            break
        fi
    done
    
    if [ "$downloaded" = false ]; then
        echo -e "${YELLOW}[FALLBACK]${NC} Creating minimal big.txt"
        create_minimal_big "$wordlist_dir/big.txt" "$use_sudo"