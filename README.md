<p align="center">
  <img src="images_readme/logo7.png" alt="Logo" width="250"/>
</p>


<p align="center">
  <img src="https://img.shields.io/badge/Version-2.4.0-red?style=for-the-badge&logo=security&logoColor=white" alt="Version">
  <img src="https://img.shields.io/badge/Platform-Linux-blue?style=for-the-badge&logo=linux&logoColor=white" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
</p>

**Security Scanner v2.4.0**: Outil avance d'evaluation red team. Concu pour les pentesteurs professionnels et chercheurs en securite.

## Nouveautes v2.4.0

### Architecture Modulaire

- **Code modularise** - Script monolithique (1,868 lignes) decoupe en 5 modules sources
  - `security` (874 lignes): Framework principal, generation de rapports, main()
  - `lib/osint.sh` (192 lignes): WHOIS, DNS, sous-domaines, crt.sh
  - `lib/network.sh` (217 lignes): Scan de ports, detection de services
  - `lib/web.sh` (229 lignes): Fingerprinting, WAF, SSL, enumeration, scan de vulns
  - `lib/exploit.sh` (415 lignes): Searchsploit, Metasploit, credentials, post-exploitation
- **Chargement flexible** - Recherche dans `$SCRIPT_DIR/lib/`, `/usr/local/lib/`, `~/.local/lib/`

### Securite Renforcee

- **Prevention XSS** - Rapports HTML avec `html.escape()` pour toutes les donnees utilisateur
- **Validation d'entree** - Fonctions `validate_ip()`, `validate_domain()`, `validate_url()`, `validate_target()`
- **Permissions securisees** - `umask 077` sur les repertoires de sortie
- **Prevention injection JSON** - Fonction `json_escape()` pour sortie JSON sure
- **Logging structure** - Journalisation horodatee dans `reports/scanner.log`

### Rapport HTML Nouvelle Generation

- **Mode clair/sombre** - Toggle avec support `prefers-color-scheme` et persistence localStorage
- **Barre de progression** - Indicateur visuel en haut de page
- **Accessibilite** - Lien skip-nav, roles ARIA, focus visible, aria-hidden sur icones decoratives
- **Recherche globale** - Filtrage de tous les resultats avec raccourci `/`
- **Filtres par severite** - Boutons (All/Critical/High/Medium) par section
- **Copie en un clic** - Bouton copier par resultat avec notification toast
- **Graphique SVG** - Donut chart de distribution des severites

### CI/CD, Docker et Tests

- **GitHub Actions CI** - ShellCheck, pylint, smoke tests, verification XSS, scan Bandit
- **32 tests unitaires** - `tests/test_html_generator.py` (tous passent)
- **ShellCheck clean** - Tous les scripts passent shellcheck
- **Docker** - Dockerfile Kali Linux + docker-compose.yml avec volume de sortie
- **Configuration** - Template `config.yml.example` avec timeouts, wordlists, cles API

## Nouveautes v2.3.4

### Corrections Critiques et Ameliorations Majeures

- **Correction timeouts scans** - Alignement des timeouts bash/nmap pour eviter interruptions
- **Amelioration detection vulnerabilites** - Scans de vulnerabilites completes meme sur cibles lentes
- **Correction affichage rapport HTML** - Section "Critical Services Detected" s'affiche correctement
- **Filtrage intelligent vulnerabilites Network** - Exclusion des messages de scan, affichage uniquement des vulnerabilites reelles
- **Timeouts optimises** - TIMEOUT_LONG passe a 900s (15 min) aligne avec nmap
- **Mode Quick corrige** - Timeouts dynamiques selon le mode choisi

## Nouveautes v2.3.3

### Optimisations Majeures et Nouvelles Fonctionnalites

- **Generation de rapports HTML** - Rapports visuels modernes et interactifs avec CSS professionnel
- **Scans parallelises** - Enumeration de subdomains en parallele (subfinder, assetfinder, findomain)
- **Scans Nmap encore plus optimises** - Coverage etendu avec --top-ports 3000, min-rate 3000
- **Timeouts dynamiques** - Timeouts adaptatifs selon le mode (quick/stealth/aggressive)
- **Performance amelioree** - Jusqu'a 30% plus rapide grace a la parallelisation

## Installation

### Installation Automatique (Recommandee)

```bash
curl -sSL https://raw.githubusercontent.com/mpgamer75/security-scanner/main/install.sh | bash
```

Cette commande unique va:
- Telecharger le script
- Installer toutes les dependances
- Configurer l'outil dans /usr/local/bin
- Rendre la commande `security` disponible globalement

### Installation via Docker

```bash
# Cloner le repository
git clone https://github.com/mpgamer75/security-scanner.git
cd security-scanner

# Lancer avec Docker Compose
docker-compose up -d

# Executer un scan
docker exec -it security-scanner security
```

### Installation Manuelle

```bash
# Cloner le repository
git clone https://github.com/mpgamer75/security-scanner.git
cd security-scanner

# Executer le script d'installation
chmod +x install.sh
./install.sh
```

L'installateur detecte automatiquement votre distribution et installe les paquets appropries.

## Demarrage Rapide

### Scan Basique

```bash
security
# Entrer l'IP cible, l'URL, le domaine
# Selectionner le type de scan (1-4)
```

### Reconnaissance Rapide

```bash
security -q
# 3x plus rapide, parfait pour une evaluation initiale
```

### Evaluation Red Team Complete

```bash
security -a
# Couverture complete: tous les ports, tous les tests, preparation exploitation
```

### Mode Furtif

```bash
security -s
# Evasion IDS/IPS, plus lent mais discret
```

## Comparaison des Performances

| Operation | v2.2.1 | v2.3.3 | v2.3.4 | v2.4.0 | Amelioration |
|-----------|--------|--------|--------|--------|-------------|
| Evaluation complete | environ 60 min | environ 14 min | environ 14 min | environ 12 min | **80% plus rapide** |
| Scan de ports | 10 min | 4 min | 4 min | 4 min | **60% plus rapide** |
| Detection services | 20 min | 4 min | 4 min | 4 min | **80% plus rapide** |
| Scan web | 15 min | 4 min | 4 min | 4 min | **73% plus rapide** |
| OSINT/Subdomains | 10 min | 3 min | 3 min | 3 min | **70% plus rapide** |
| Generation rapport | 75% succes | 100% succes | 100% succes | 100% succes | **+25%** |
| Fiabilite scans | 85% | 95% | 100% | 100% | **+15%** |
| Detection vulns | Variable | Bonne | Excellente | Excellente | **Aucun faux negatif** |

## Prerequis

### Outils Principaux (Auto-installes)

```bash
# Outils reseau
nmap masscan

# Outils web
gobuster nikto whatweb sqlmap

# Outils OSINT
whois subfinder theHarvester

# Scanners de vulnerabilites
nuclei
```

### Installation

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nmap masscan gobuster sqlmap whois nikto whatweb

# Outils Go (versions pinees)
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@v2.6.6
go install github.com/projectdiscovery/nuclei/v2/cmd/nuclei@v3.2.4

# Outils Python
pip3 install theHarvester
```

## Fonctionnalites Principales

### 1. OSINT et Collecte d'Informations

- **Enumeration rapide de sous-domaines** (Subfinder, Assetfinder, Findomain)
- **Collecte d'emails** (theHarvester)
- **Transparence des certificats** (crt.sh)
- **Enumeration DNS** (dig)
- **Google dorking** (requetes automatisees)
- **Reconnaissance reseaux sociaux**

### 2. Reconnaissance Reseau

- **Scan de ports optimise** (-Pn force, timeouts intelligents)
- **Detection de services** (scripts NSE Nmap)
- **Empreinte OS**
- **Detection de vulnerabilites** (scripts vuln)
- **Enumeration SMB** (enum4linux, smbclient)
- **Enumeration SNMP**

### 3. Tests d'Applications Web

- **Empreinte technologique** (WhatWeb, Wappalyzer)
- **Detection WAF** (wafw00f)
- **Enumeration de repertoires** (Gobuster)
- **Scan de vulnerabilites** (Nuclei, Nikto)
- **Analyse SSL/TLS**
- **Tests d'injection SQL** (SQLMap)

### 4. Preparation a l'Exploitation

- **Recherche base exploits** (searchsploit)
- **Preparation modules Metasploit**
- **Analyse surface d'attaque**
- **Listes de credentials** (mots de passe par defaut)
- **Scripts d'attaque automatises**
- **Checklist post-exploitation**

## Structure des Resultats

```
redteam_20260322_143022/
├── osint/
│   ├── whois.txt
│   ├── dns.txt
│   ├── subdomains_subfinder.txt
│   ├── all_subdomains.txt          # Consolide
│   ├── emails.txt
│   ├── crt_sh.txt
│   └── google_dorks.txt
├── network/
│   ├── nmap_ports.txt              # Scan de ports
│   ├── nmap_services.txt           # Detection services
│   ├── nmap_vulns.txt              # Vulnerabilites
│   ├── nmap_os.txt                 # Detection OS
│   ├── smb_enum.txt                # Enumeration SMB
│   └── snmp_enum.txt
├── web/
│   ├── whatweb.txt
│   ├── wafw00f.txt
│   ├── ssl_analysis.txt
│   ├── gobuster.txt
│   ├── nuclei.txt
│   └── nikto.txt
├── exploit/
│   ├── searchsploit.txt
│   ├── attack_surface.txt
│   ├── auto_attack.sh
│   └── credentials.txt
└── reports/
    ├── summary_report.txt          # Rapport texte complet
    ├── assessment.json             # Lisible machine
    ├── assessment.html             # Rapport HTML interactif
    └── scanner.log                 # Journal horodate
```

## Exemples d'Utilisation

### Exemple 1: Evaluation Web Complete

```bash
security

IP cible: 192.168.1.100
URL cible: https://example.com
Domaine: example.com

Selectionner: [4] Evaluation Red Team Complete

Resultats dans: redteam_20260322_143022/
```

### Exemple 2: Scan Reseau Rapide

```bash
security -q

IP cible: 10.0.0.50
Selectionner: [2] Reconnaissance Reseau

# 3x plus rapide que le mode standard
```

### Exemple 3: OSINT Furtif

```bash
security -s

IP cible: 203.0.113.10
Domaine: target.com
Selectionner: [1] OSINT et Collecte d'Informations

# Lent et discret, evite la detection
```

### Exemple 4: Scan Docker

```bash
docker-compose run --rm scanner security -a

# Environnement isole avec tous les outils pre-installes
```

## Configuration Avancee

### Timeouts Personnalises

Editer `/usr/local/bin/security`:

```bash
# Ligne environ 43-47 (v2.4.0 - Optimises et exportes)
export TIMEOUT_VERY_SHORT=15
export TIMEOUT_SHORT=30
export TIMEOUT_MEDIUM=120
export TIMEOUT_LONG=900        # 15 min - aligne avec nmap --host-timeout 15m
export TIMEOUT_VERY_LONG=1200  # 20 min - pour scans de vulnerabilites complexes
```

### Configuration YAML (Nouveau)

```bash
cp config.yml.example config.yml
# Editer config.yml avec vos preferences:
# - Timeouts personnalises
# - Chemins wordlists
# - Cles API (Shodan, etc.)
# - Profils de scan
```

### Wordlists Personnalisees

```bash
# Utiliser votre propre wordlist
export CUSTOM_WORDLIST="/chemin/vers/wordlist.txt"
gobuster dir -u $URL -w $CUSTOM_WORDLIST
```

## Fonctionnalites Anti-Blocage

### 1. -Pn Force (Pas de Ping)

Tous les scans Nmap utilisent `-Pn` pour eviter le blocage sur les hotes non-pingables:

```bash
nmap -Pn -sS $target  # Fonctionne toujours, jamais bloque
```

### 2. Timeouts Intelligents

```bash
--host-timeout 5m     # Max 5min par hote
--max-retries 1       # Seulement 1 retry
--min-rate 2000       # Minimum 2000 paquets/sec
```

### 3. Contournement Rate Limiting

```bash
--defeat-rst-ratelimit  # Contourne la limitation de taux RST
```

### 4. Mecanismes de Secours

Si un outil echoue, le scan continue avec des outils ou methodes alternatifs.

## Bonnes Pratiques de Securite

### Usage Legal

- **Tester uniquement vos propres systemes**
- **Obtenir une autorisation ecrite** avant tout test
- **Respecter le perimetre et les regles d'engagement**
- **Ne jamais tester sans permission**

### Securite Operationnelle

```bash
# Utiliser un VPN
openvpn --config vpn.conf

# Verifier votre IP
curl ifconfig.me

# Utiliser proxychains (optionnel)
proxychains security
```

### Divulgation Responsable

Si vous trouvez des vulnerabilites:

1. Documenter tout
2. Contacter le fournisseur/organisation
3. Donner un delai raisonnable pour corriger (90 jours)
4. Divulguer de maniere responsable

## Depannage

### Scans Trop Lents?

```bash
# Utiliser le mode rapide
security -q

# Ou reduire les timeouts
sudo nano /usr/local/bin/security
# Editer les variables TIMEOUT_*
```

### Scans Bloquent/Se Figent?

```bash
# Verifier que -Pn est present
grep "nmap -Pn" /usr/local/bin/security

# Mettre a jour vers la derniere version
curl -sSL https://raw.githubusercontent.com/mpgamer75/security-scanner/main/security -o /tmp/security_new
sudo mv /tmp/security_new /usr/local/bin/security
sudo chmod +x /usr/local/bin/security
```

### Rapports Non Generes?

```bash
# Verifier les fichiers individuels
find redteam_* -name "*.txt" -size +0

# Verifier les permissions
ls -la redteam_*/reports/

# Consulter le journal
cat redteam_*/reports/scanner.log
```

### Outil Non Trouve?

```bash
# Installer les outils manquants
sudo apt install nmap gobuster nikto

# Verifier l'installation
which nmap subfinder nuclei

# Reinstaller si necessaire
./install.sh
```

## Feuille de Route

### Version 2.5.0 (Planifiee)

- Correlation de vulnerabilites par apprentissage automatique
- Tableau de bord web (monitoring temps reel)
- Export PDF avec graphiques
- Integration directe Metasploit
- Support GNU Parallel (scans reseau parallelises)

### Version 3.0.0 (Future)

- Scan distribue (multi-hote)
- API REST pour l'automatisation
- Integration pipeline CI/CD avancee
- Deploiement cloud natif

## Contribuer

Les contributions sont bienvenues! Voici comment:

1. Fork le repository
2. Creer une branche feature (`git checkout -b feature/amelioration-geniale`)
3. Commiter les changements (`git commit -m 'Ajout fonctionnalite geniale'`)
4. Push vers la branche (`git push origin feature/amelioration-geniale`)
5. Ouvrir une Pull Request

### Directives de Developpement

- Tester sur Ubuntu 22.04 et Kali Linux
- Suivre les bonnes pratiques bash (ShellCheck clean)
- Documenter les nouvelles fonctionnalites
- Maintenir la retrocompatibilite
- Ajouter des tests unitaires

## Licence

Licence MIT - voir le fichier [LICENSE](LICENSE)

## Auteur

**mpgamer75**

- GitHub: [@mpgamer75](https://github.com/mpgamer75)
- Expertise: Cybersecurite, Tests d'Intrusion, Operations Red Team

## Remerciements

- [ProjectDiscovery](https://github.com/projectdiscovery) - Subfinder, Nuclei
- [OWASP](https://owasp.org/) - Ressources de securite
- [SecLists](https://github.com/danielmiessler/SecLists) - Wordlists
- [Nmap](https://nmap.org/) - Scan reseau
- Communaute open source securite

## Support

Besoin d'aide?

1. Consulter la [section depannage](#depannage)
2. Lire la [documentation](README_EN.md)
3. Chercher dans les [issues existantes](https://github.com/mpgamer75/security-scanner/issues)
4. Ouvrir une [nouvelle issue](https://github.com/mpgamer75/security-scanner/issues/new)

---

<p align="center">
  <strong>Security Scanner v2.4.0</strong><br>
  Outil Professionnel d'Evaluation Red Team<br>
  Rapide - Fiable - Complet
</p>
