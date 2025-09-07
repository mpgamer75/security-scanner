<p align="center">
  <img src="images_readme/logo7.png" alt="Logo" width="250"/>
</p>


<p align="center">
  <img src="https://img.shields.io/badge/Version-2.0.0-red?style=for-the-badge&logo=security&logoColor=white" alt="Version">
  <img src="https://img.shields.io/badge/Platform-Linux-blue?style=for-the-badge&logo=linux&logoColor=white" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

**Security Scanner** : un outil de reconnaissance et d'évaluation de sécurité avancé qui automatise les phases d'OSINT, de reconnaissance réseau et de test d'applications web. Conçu pour les professionnels de la cybersécurité, les pentesters et les bug hunters.

## Installation


### Installation Automatique (Recommandée)

```bash
curl -sSL https://raw.githubusercontent.com/mpgamer75/security-scanner/main/install.sh | bash
```

### Installation Manuelle

1. **Cloner le repository**

```bash
git clone https://github.com/mpgamer75/security-scanner.git
cd security-scanner
```

2. **Installer les dépendances**

```bash
chmod +x install.sh
./install.sh
```

3. **Installation globale**

```bash
sudo chmod +x security
sudo mv security /usr/local/bin/
```

### Désinstallation

Pour désinstaller complètement Security Scanner :

```bash
curl -sSL https://raw.githubusercontent.com/mpgamer75/security-scanner/main/uninstall.sh | bash
```

Ou pour une désinstallation manuelle :

```bash
# Supprimer l'exécutable
sudo rm -f /usr/local/bin/security

# Supprimer l'entrée du bureau
rm -f ~/.local/share/applications/security-scanner.desktop

# Supprimer les outils Go (optionnel)
rm -f $(go env GOPATH)/bin/{subfinder,nuclei,amass,assetfinder}
```

**Note :** La désinstallation ne supprime pas automatiquement les résultats de scan ni les wordlists pour préserver vos données.

## Prérequis

### Outils Principaux

- `nmap` - Scanner de ports et de services
- `masscan` - Scanner haute vitesse
- `subfinder` - Découverte de sous-domaines
- `gobuster` - Brute force de répertoires
- `sqlmap` - Détection d'injections SQL
- `theharvester` - Collecte d'emails et d'informations
- `whois` - Informations de domaine
- `nikto` - Scanner de vulnérabilités web
- `whatweb` - Identification de technologies
- `nuclei` - Scanner de vulnérabilités moderne

### Installation des Outils (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install nmap masscan gobuster sqlmap whois nikto whatweb dig openssl

# Installation des outils Go
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest
```

## Fonctionnalités Principales

### OSINT & Collecte d'Informations

- **Recherche WHOIS** - Informations sur la propriété du domaine
- **Énumération DNS** - Records A, MX, NS, TXT
- **Analyse de certificats SSL** - Détails des certificats
- **Découverte de sous-domaines** - Via Subfinder
- **Collecte d'emails** - TheHarvester integration

### Reconnaissance Réseau

- **Scan de ports optimisé** - Nmap avec profils de performance
- **Détection de services** - Identification des versions
- **Fingerprinting OS** - Identification du système d'exploitation
- **Scan UDP** - Ports UDP critiques
- **Masscan ultra-rapide** - Scan haute vitesse

### Tests d'Applications Web

- **Énumération de répertoires** - Gobuster avec wordlists multiples
- **Scan de vulnérabilités** - Nikto et Nuclei
- **Tests d'injection SQL** - SQLMap automatisé
- **Identification technologique** - WhatWeb analysis

### Rapports & Organisation

- **Rapports structurés** - Résumé exécutif détaillé
- **Organisation par catégories** - OSINT, Network, Web
- **Format timestamp** - Horodatage des scans
- **Analyse rapide** - Résumé des découvertes clés

## Utilisation

### Mode Interactif

```bash
security
```

### Options en Ligne de Commande

```bash
security --help      # Afficher l'aide
security --version   # Afficher la version
```

### Flux de Travail Typique

1. **Lancement du scanner**

   ```bash
   security
   ```

2. **Saisie des informations cibles**
   - Adresse IP cible
   - URL (optionnel)
   - Nom de domaine (optionnel)

3. **Sélection du type de scan**
   - OSINT & Collecte d'informations
   - Reconnaissance réseau
   - Tests d'applications web
   - Scan complet
   - Sélection personnalisée

4. **Analyse des résultats**
   - Consultez le rapport dans `recon_YYYYMMDD_HHMMSS/`
   - Résumé exécutif disponible dans `reports/executive_summary.txt`

## Structure des Résultats

```
security_scan_20250907_143022/
├── osint/
│   ├── whois.txt           # Informations WHOIS
│   ├── dns_enum.txt        # Énumération DNS standard
│   ├── dnsenum.txt         # DNSEnum avancé
│   ├── dnsrecon.txt        # Reconnaissance DNS
│   ├── emails.txt          # Emails collectés
│   └── reverse_dns.txt     # DNS inversé
├── domains/
│   ├── subdomains_subfinder.txt  # Sous-domaines (Subfinder)
│   ├── subdomains_amass.txt      # Sous-domaines (Amass)  
│   ├── subdomains_assetfinder.txt # Sous-domaines (Assetfinder)
│   ├── all_subdomains.txt        # Consolidation de tous les sous-domaines
│   ├── ssl_cert.txt              # Analyse certificat SSL
│   ├── sslscan.txt               # Configuration SSL
│   ├── whatweb.txt               # Technologies détectées
│   └── wafw00f.txt               # Détection WAF
├── network/
│   ├── nmap_fast.txt       # Scan rapide Nmap
│   ├── nmap_full.txt       # Scan complet Nmap
│   ├── nmap_udp.txt        # Scan UDP
│   ├── nmap_os.txt         # Fingerprinting OS
│   ├── masscan.txt         # Résultats Masscan
│   └── unicornscan_tcp.txt # Unicornscan TCP
├── web/
│   ├── gobuster_common.txt # Répertoires (wordlist commune)
│   ├── gobuster_big.txt    # Répertoires (wordlist étendue)
│   ├── dirb.txt            # Énumération Dirb
│   ├── nikto.txt           # Vulnérabilités web
│   ├── nuclei.txt          # Templates Nuclei
│   └── sqlmap/             # Résultats SQLMap
└── reports/
    └── executive_summary.txt # Rapport de synthèse formaté
```

## Exemples d'Utilisation

### Scan OSINT Complet

```bash
# Collecte d'informations sur un domaine
Target: example.com
Options: 1 (OSINT & Information Gathering)
```

### Reconnaissance Réseau Approfondie

```bash
# Scan réseau d'une adresse IP
Target: 192.168.1.100
Options: 2 (Network Reconnaissance)
```

### Test d'Application Web

```bash
# Test de sécurité d'une application web
Target: https://example.com
Options: 3 (Web Application Testing)
```

### Audit de Sécurité Complet

```bash
# Évaluation complète (OSINT + Network + Web)
Target IP: 192.168.1.100
Target URL: https://example.com
Domain: example.com
Options: 4 (All scans)
```

## Configuration Avancée

### Optimisation des Performances

**Nmap Ultra-Rapide**

```bash
# Modification dans le script pour scan très rapide
nmap -n -T5 --min-rate=5000 --max-retries=1
```

**Masscan Haute Vitesse**

```bash
# Configuration pour réseaux rapides
masscan --rate=100000 --wait=0
```

### Wordlists Personnalisées

```bash
# Utilisation de wordlists personnalisées
export CUSTOM_WORDLIST="/path/to/custom/wordlist.txt"
```

## Considérations de Sécurité

### Utilisation Légale

- Utilisez uniquement sur vos propres systèmes
- Obtenez une autorisation écrite avant tout test
- Respectez les conditions d'utilisation des services
- N'utilisez jamais sur des systèmes sans autorisation

### Bonnes Pratiques

- Limitez la vitesse de scan sur les réseaux partagés
- Utilisez des VPN pour les tests externes
- Documentez toutes les activités de test
- Respectez les politiques de divulgation responsable

## Avertissements

> **IMPORTANT**: Cet outil est destiné aux professionnels de la sécurité autorisés. L'utilisation non autorisée de cet outil peut violer les lois locales et internationales. L'auteur décline toute responsabilité en cas d'utilisation malveillante.

## Dépannage

### Problèmes Courants

**Erreur: "Tool not found"**

```bash
# Vérifier l'installation des outils
security --help
which nmap subfinder gobuster
```

**Scans lents**

```bash
# Vérifier la connectivité réseau
ping 8.8.8.8
# Ajuster les paramètres de timing Nmap
```

**Permissions insuffisantes**

```bash
# Certains scans nécessitent des privilèges root
sudo security
```

## Améliorations Futures

### Version 2.1.0 (Prévue)

- [ ] Interface web optionnelle
- [ ] Intégration avec Metasploit
- [ ] Scan de vulnérabilités IoT
- [ ] Export vers formats multiples (JSON, XML, CSV)
- [ ] Notifications en temps réel

### Version 2.2.0 (Planifiée)

- [ ] Mode distribué pour scans à grande échelle
- [ ] Intégration intelligence threat
- [ ] Automatisation via API REST
- [ ] Dashboard de monitoring

## Contribution

Les contributions sont les bienvenues ! Voici comment contribuer :

1. **Fork** le projet
2. **Créer** une branche feature (`git checkout -b feature/amelioration`)
3. **Commit** vos changements (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. **Push** vers la branche (`git push origin feature/amelioration`)
5. **Ouvrir** une Pull Request

### Guidelines de Contribution

- Suivre les conventions de nommage existantes
- Documenter les nouvelles fonctionnalités
- Tester sur plusieurs distributions Linux
- Respecter le style de code bash

## Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## Auteur

**mpgamer75**

- GitHub: [@mpgamer75](https://github.com/mpgamer75)
- Spécialité: Cybersécurité

## Remerciements

- [ProjectDiscovery](https://github.com/projectdiscovery) pour Subfinder et Nuclei
- [OWASP](https://owasp.org/) pour les ressources de sécurité
- [SecLists](https://github.com/danielmiessler/SecLists) pour les wordlists
- La communauté open source pour les outils de sécurité

## Support

Pour obtenir de l'aide :

1. Consultez la [documentation](README.md)
2. Vérifiez les [issues existantes](https://github.com/mpgamer75/security-scanner/issues)
3. Ouvrez une [nouvelle issue](https://github.com/mpgamer75/security-scanner/issues/new)

---

<p align="center">
  <strong>Security Scanner - Professional Security Assessment Tool</strong>
</p>