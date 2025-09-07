#!/bin/bash

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

echo -e "${CYAN}[INFO]${NC} Installing Security Scanner..."

# Vérifie les prérequis
if ! command -v curl &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} curl is required but not installed."
    exit 1
fi

# Télécharge le script principal
echo -e "${CYAN}[INFO]${NC} Downloading Security Scanner..."
if ! curl -sSL -o security "https://raw.githubusercontent.com/mpgamer75/security-scanner/main/security"; then
    echo -e "${RED}[ERROR]${NC} Failed to download security script"
    exit 1
fi

# Rendre exécutable
chmod +x security

# Installe globalement
echo -e "${CYAN}[INFO]${NC} Installing globally..."
if sudo mv security /usr/local/bin/; then
    echo -e "${GREEN}[SUCCESS]${NC} Security Scanner installed successfully!"
    echo -e "${WHITE}You can now run:${NC} ${CYAN}security${NC}"
else
    echo -e "${RED}[ERROR]${NC} Installation failed"
    exit 1
fi

# Vérifie les outils de base
echo -e "${CYAN}[INFO]${NC} Checking basic tools..."
missing_tools=()

for tool in nmap whois dig openssl; do
    if ! command -v "$tool" &> /dev/null; then
        missing_tools+=("$tool")
    fi
done

if [ ${#missing_tools[@]} -gt 0 ]; then
    echo -e "${YELLOW}[WARNING]${NC} Missing tools: ${missing_tools[*]}"
    echo -e "${YELLOW}[INFO]${NC} Install them with your package manager:"
    
    if command -v apt &> /dev/null; then
        echo -e "${WHITE}sudo apt update && sudo apt install -y ${missing_tools[*]}${NC}"
    elif command -v yum &> /dev/null; then
        echo -e "${WHITE}sudo yum install -y ${missing_tools[*]}${NC}"
    elif command -v pacman &> /dev/null; then
        echo -e "${WHITE}sudo pacman -S ${missing_tools[*]}${NC}"
    fi
fi

echo -e "${GREEN}[COMPLETED]${NC} Installation finished!"
echo -e "${YELLOW}Note: The scanner will offer to install missing tools and wordlists when needed${NC}"