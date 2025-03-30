#!/bin/bash


RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "  _____                       _ _           _____                  "
echo " / ____|                     (_) |         / ____|                 "
echo "| (___   ___  ___ _   _ _ __ _| |_ _   _ | (___   ___ __ _ _ __   "
echo " \___ \ / _ \/ __| | | | '__| | __| | | | \___ \ / __/ _\` | '_ \  "
echo " ____) |  __/ (__| |_| | |  | | |_| |_| | ____) | (_| (_| | | | | "
echo "|_____/ \___|\___|\__,_|_|  |_|\__|\__, ||_____/ \___\__,_|_| |_| "
echo "                                     __/ |                         "
echo "                                    |___/                          "
echo -e "${NC}"
echo -e "${YELLOW}Installation du script Security Scanner${NC}"
echo -e "${GREEN}Développé par mpgamer75${NC}"
echo -e "${BLUE}------------------------------------------${NC}"
echo ""

# check si tous les outils sont bien présents
echo -e "${BLUE}[INFO] Vérification des outils requis...${NC}"

MISSING_TOOLS=()

for tool in nmap dirb nikto gobuster sqlmap; do
    if ! command -v $tool &> /dev/null; then
        MISSING_TOOLS+=($tool)
    fi
done

if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
    echo -e "${YELLOW}[ATTENTION] Les outils suivants ne sont pas installés:${NC}"
    for tool in "${MISSING_TOOLS[@]}"; do
        echo -e "  - $tool"
    done
    
    echo -e "${BLUE}Voulez-vous installer les outils manquants maintenant? (o/n)${NC}"
    read -r INSTALL_TOOLS
    
    if [[ "$INSTALL_TOOLS" == "o" || "$INSTALL_TOOLS" == "O" || "$INSTALL_TOOLS" == "oui" ]]; then
        echo -e "${BLUE}[INFO] Installation des outils manquants...${NC}"
        sudo apt update
        sudo apt install -y "${MISSING_TOOLS[@]}"
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}[SUCCÈS] Tous les outils requis sont maintenant installés.${NC}"
        else
            echo -e "${RED}[ERREUR] L'installation a échoué. Veuillez installer manuellement les outils manquants.${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}[ATTENTION] Certains outils requis ne sont pas installés. Le script pourrait ne pas fonctionner correctement.${NC}"
    fi
else
    echo -e "${GREEN}[OK] Tous les outils requis sont déjà installés.${NC}"
fi

# Télécharge le script
echo -e "${BLUE}[INFO] Téléchargement du script Security Scanner...${NC}"
curl -sSL https://raw.githubusercontent.com/mpgamer75/security-scanner/main/security -o security

if [ $? -ne 0 ]; then
    echo -e "${RED}[ERREUR] Échec du téléchargement du script.${NC}"
    exit 1
fi

# Classique ==> rend le script exécutable
chmod +x security

# ça l'envoie à ==> /usr/local/bin
echo -e "${BLUE}[INFO] Installation du script dans /usr/local/bin/...${NC}"
sudo mv security /usr/local/bin/

if [ $? -eq 0 ]; then
    echo -e "${GREEN}[SUCCÈS] Le script Security Scanner a été installé avec succès!${NC}"
    echo -e "${BLUE}Vous pouvez maintenant lancer le script en tapant simplement '${GREEN}security${BLUE}' dans votre terminal.${NC}"
else
    echo -e "${RED}[ERREUR] L'installation a échoué. Vous pouvez essayer de l'installer manuellement:${NC}"
    echo -e "${YELLOW}sudo mv security /usr/local/bin/${NC}"
fi