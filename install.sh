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
    
    local tools=(nmap masscan gobuster sqlmap whois nikto whatweb dig openssl curl wget git python3-pip)
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
    
    # Install Python tools
    echo -e "${CYAN}[INFO]${NC} Installing Python-based tools..."
    
    if command -v pip3 &> /dev/null; then
        # Install theHarvester
        if ! command -v theHarvester &> /dev/null; then
            echo -e "${CYAN}[INFO]${NC} Installing theHarvester..."
            pip3 install theHarvester --break-system-packages 2>/dev/null || pip3 install theHarvester
        fi
        
        # Install other useful Python tools
        if ! command -v shodan &> /dev/null; then
            echo -e "${CYAN}[INFO]${NC} Installing Shodan CLI..."
            pip3 install shodan --break-system-packages 2>/dev/null || pip3 install shodan
        fi
    else
        echo -e "${YELLOW}[WARNING]${NC} pip3 not found. Some Python tools will not be installed."
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
    
    # Vérifier si on peut écrire dans /usr/share/wordlists
    if [ ! -d "$wordlist_dir" ]; then
        if ! sudo mkdir -p "$wordlist_dir" 2>/dev/null; then
            wordlist_dir="$HOME/.local/share/wordlists/dirb"
            mkdir -p "$wordlist_dir"
            use_sudo=false
            echo -e "${YELLOW}[INFO]${NC} Using local wordlist directory: $wordlist_dir"
        fi
    fi
    
    # Vérifier si les wordlists existent déjà
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
    
    # Télécharger common.txt
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
    
    # Télécharger big.txt
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
    fi
    
    echo -e "${GREEN}[COMPLETED]${NC} Wordlists setup completed"
}

create_minimal_common() {
    local output="$1"
    local use_sudo="$2"
    
    local content="admin
administrator
index
login
home
about
contact
news
blog
search
images
img
css
js
api
upload
download
backup
config
tmp
temp
files
data
test
admin.php
login.php
index.php
config.php
backup.sql
database
db
phpinfo
info
server-info
server-status
robots.txt
sitemap.xml"
    
    if [ "$use_sudo" = true ]; then
        echo "$content" | sudo tee "$output" > /dev/null
    else
        echo "$content" > "$output"
    fi
}

create_minimal_big() {
    local output="$1"
    local use_sudo="$2"
    
    local content="admin
administration
administrator
api
app
application
apps
archive
archives
backup
backups
bin
blog
cache
cgi-bin
config
configuration
css
data
database
db
demo
dev
development
doc
docs
download
downloads
email
error
errors
example
examples
file
files
forum
ftp
home
html
http
https
image
images
img
include
includes
index
info
install
installation
js
lib
libs
log
logs
mail
media
member
members
news
old
page
pages
php
phpmyadmin
pics
private
public
root
script
scripts
search
secure
security
site
sites
src
stat
static
stats
support
sys
system
temp
template
templates
test
testing
tests
tmp
tools
upload
uploads
user
users
var
web
webmail
www
.htaccess
.git
.svn
administrator/
admin/
login/
wp-admin/
wp-content/
wp-includes/
wp-config.php
readme.txt
license.txt
changelog.txt
version.txt"
    
    if [ "$use_sudo" = true ]; then
        echo "$content" | sudo tee "$output" > /dev/null
    else
        echo "$content" > "$output"
    fi
}

install_nuclei_templates() {
    echo -e "${CYAN}[INFO]${NC} Setting up Nuclei templates..."
    
    if command -v nuclei &> /dev/null; then
        echo -e "${CYAN}[INFO]${NC} Updating Nuclei templates..."
        nuclei -update-templates &> /dev/null
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}[OK]${NC} Nuclei templates updated"
        else
            echo -e "${YELLOW}[WARNING]${NC} Failed to update Nuclei templates automatically"
        fi
    else
        echo -e "${YELLOW}[WARNING]${NC} Nuclei not found, skipping template update"
    fi
}

install_scanner() {
    echo -e "${CYAN}[INFO]${NC} Installing Security Scanner..."
    
    # Download the main script
    if ! curl -sSL https://raw.githubusercontent.com/mpgamer75/security-scanner/main/security -o security; then
        echo -e "${RED}[ERROR]${NC} Failed to download scanner script"
        exit 1
    fi
    
    # Make executable
    chmod +x security
    
    # Install globally
    if sudo mv security /usr/local/bin/; then
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
    install_wordlists
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
    echo -e "${WHITE}Features installed:${NC}"
    echo -e "  ${GREEN}✓${NC} Security Scanner executable"
    echo -e "  ${GREEN}✓${NC} Required security tools"
    echo -e "  ${GREEN}✓${NC} Wordlists for web scanning"
    if command -v nuclei &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} Nuclei templates"
    fi
    if command -v subfinder &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} Go-based tools (subfinder, nuclei, etc.)"
    fi
    echo
    echo -e "${YELLOW}Note: Use responsibly and only on systems you own or have permission to test${NC}"
    echo
}

# Execute main function
main "$@"